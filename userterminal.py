import bluetooth
import time
import message_codecs as mc
import queue
import json
import multiprocessing as mp

LOOP_BACKOFF = 0.001
BUFFER_SIZE = 8192

class UserTerminal(mp.Process):
    rx_timeout = 0.05
    def _subproc(self, cfg_bt, my_q, mgr_q, log):
        server = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        server.bind(('', cfg_bt['port']))

        server.listen(1)
        server.setblocking(False)

        log.debug("Bluetooth listening for connection")
        client = None
        while True:
            do_loop_delay = True    # Used to determine if I put a delay at the end of the loop.

            if client is None:
                # Check if there's a connection request from a client
                try:
                    client, clientaddr = server.accept()
                except bluetooth.btcommon.BluetoothError as e:
                    errno = eval(e.args[0])[0]
                    if errno != 11:
                        raise e
                else:
                    if client is not None:
                        client.setblocking(False)
                        log.info(f"Bluetooth client {clientaddr} connected")

            if client is not None:
                # Check if there's data in the input buffer, if not, skip the reading
                try:
                    pkt = client.recv(BUFFER_SIZE)
                except bluetooth.btcommon.BluetoothError as e:
                    errno = eval(e.args[0])[0]
                    if errno != 11:
                        # client got disconnected
                        client = None
                else:
                    # If there was data in the input buffer, keep reading until the packet data gets tranferred completely.
                    # The packet is considered finished when I don't receive any data for self.rx_timeout seconds.
                    lastrxtime = time.time()
                    while time.time() - lastrxtime < self.rx_timeout:
                        try:
                            pkt += client.recv(BUFFER_SIZE)
                        except bluetooth.btcommon.BluetoothError as e:
                            errno = eval(e.args[0])[0]
                            if errno != 11:
                                # Any errno other than 11 (Resource unavailable) is considered as a client disconnection.
                                client = None
                                break
                            else:
                                time.sleep(LOOP_BACKOFF)
                        else:
                            lastrxtime = time.time()
                    else:
                        # If the while loop finishes normally (by timeout), it means we have an input packet
                        do_loop_delay = False
                        try:
                            msg = mc.parse_json(pkt)
                        except json.decoder.JSONDecodeError as e:
                            mgr_q.put({
                                'type': 'user_received_malformed',
                                'msg': pkt,
                                'error': str(e)
                            })
                        except KeyError as e:
                            mgr_q.put({
                                'type': 'user_received_malformed',
                                'msg': pkt,
                                'error': f"Message key {str(e)} missing"
                            })
                        except Exception as e:
                            self.log.error(f"Exception raised: {e.args}")
                        else:
                            mgr_q.put({
                                'type': 'user_received',
                                'msg': msg
                            })

            # Check if there's a message in the outbound queue
            try:
                msg = my_q.get_nowait()
            except queue.Empty:
                pass
            else:
                msg_sent = False

                # If a message needs to be sent, check if the client is connected
                if client is not None:
                    do_loop_delay = False

                    try:
                        client.send(msg.as_json())
                    except bluetooth.btcommon.BluetoothError as e:
                        log.warning(f"Error sending message to remote device: {str(e)}")
                    else:
                        msg_sent = True

                if not msg_sent:
                    mgr_q.put({
                        'type': 'user_undelivered',
                        'msg': msg
                    })

            if do_loop_delay:
                time.sleep(LOOP_BACKOFF)
            
    def __init__(self, cfg_bt, mgr_q, log):
        self._proc_q = mp.Queue()
        self.send = self._proc_q.put
        self.log = log
        super().__init__(target=self._subproc, args=(cfg_bt, self._proc_q, mgr_q, log))
        super().start()
