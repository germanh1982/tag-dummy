#!/usr/bin/python3
import argparse
import multiprocessing as mp
import json
import message_codecs as mc
from time import sleep, time
import logging
import queue
import random
import threading
import os
from userterminal import UserTerminal

"""
Counter class, increments its value automatically on each read.
"""
class Counter():
    def __init__(self):
        self._x = 0

    @property
    def value(self):
        x = self._x
        self._x += 1
        return x

class KeyboardReader(threading.Thread):
    def keyb_read(self, evtqueue):
        print("cmd>", end=" ")
        while True:
            try:
                cmd = input()
            except EOFError:
                print("Received EOF")
            else:
                evtqueue.put(cmd)
                print("cmd>", end=" ")

    def __init__(self, evtqueue):
        self._keybproc = threading.Thread(target=self.keyb_read, args=(evtqueue,))
        self._keybproc.daemon = True    # Set as daemon so the thread gets killed when parent terminates
        self._keybproc.start()

"""
Main program
"""
class Main():
    def __init__(self):
        # Parse command line arguments
        p = argparse.ArgumentParser()
        p.add_argument('--config', '-c', help="Configuration file", default="/etc/tag-dummy.json")
        p.add_argument('--loglevel', '-l', choices=['debug', 'info', 'warning', 'error', 'critical'], default='debug', help="Logging level")
        args = p.parse_args()

        # Read configuration
        with open(args.config) as cfgh:
            self.cfg = json.load(cfgh)

        # Set up logging
        logging.basicConfig(format='%(asctime)-15s %(levelname)s %(message)s')
        self.log = logging.getLogger()
        self.log.setLevel(args.loglevel.upper())

        self._mq = mp.Queue()   # Main queue
        self.ut = UserTerminal(self.cfg['bluetooth'], self._mq, self.log)

        self.checklists = []
        self.create_new_checklist()

        self.keyb_queue = queue.Queue()
        self.keyboard_reader = KeyboardReader(self.keyb_queue)

    def cmd_interpreter(self, cmd):
        # Update the checklist and send it to the user terminal
        if cmd == "update checklist":
            self.create_new_checklist()

        # Send a question to the user terminal
        elif cmd.find("question ") == 0:
            question_text, *responses = cmd[len("new-question "):].split(',')
            question_data = {
                'text': question_text,
                'responses': dict(zip(range(len(responses)), responses))
            }
            msg = mc.MsgUserQuestion({'question_id': os.urandom(1)[0], 'user_question': question_data})
            self.log.info(f"Sending user_question: {msg.as_dict()}")
            self.ut.send(msg.as_json().encode())

        elif cmd.find("send checklist version") == 0:
            msg = mc.MsgChecklistVersionNotification({'checklist_version': len(self.checklists)})
            self.log.info(f"Sending {msg.as_dict()}")
            self.ut.send(msg.as_json().encode())

        else:
            self.log.warning(f"Unknown command {cmd}")

    def check_for_keyboard_cmd(self):
        try:
            cmd = self.keyb_queue.get_nowait()
        except queue.Empty:
            pass
        else:
            self.log.debug(cmd)
            self.cmd_interpreter(cmd)

    def send_current_checklist(self):
        # Send ChecklistUpdate
        checklist_dict = [self.cfg['checklist_questions'][i] for i in self.picked_questions]
        checklist_msg = mc.MsgChecklistUpdate({
            'checklist_version': len(self.checklists),
            'checklist_data': checklist_dict
        })
        self.log.info(checklist_msg.as_json())
        self.ut.send(checklist_msg)

    def create_new_checklist(self):
        # Pick some questions from the set
        self.picked_questions = random.sample(range(len(self.cfg['checklist_questions'])), self.cfg['checklist_num_questions'])
        # Keep checklist in local storage, to be able to check against it in future MsgChecklistResponse messages
        self.checklists.append(self.picked_questions)
        # Send checklist to terminal
        self.send_current_checklist()
        
    def process_msg_from_terminal(self, msg):
        # MsgLoginRequest
        if isinstance(msg, mc.MsgLoginRequest):
            if str(msg.uid.value) in self.cfg['userdb']:
                # If user valid, reply login ok
                self.log.info(f"User {msg.uid.value} valid!")
                userinfo = self.cfg['userdb'][str(msg.uid.value)]
                self.ut.send(mc.MsgLoginResponse({ 'response': True, 'uid': msg.uid.value, 'username': userinfo['username'], 'profile': userinfo['profile'] }))
                del userinfo
            else:
                # If user not in database, reply login error
                self.log.info(f"User {msg.uid.value} invalid!")
                self.ut.send(mc.MsgLoginResponse({ 'response': False, 'uid': msg.uid.value, 'username': "", 'profile': 255 }))

        # MsgSetBlockStatus
        elif isinstance(msg, mc.MsgSetBlockStatus):
            print("Vehicle", "blocked" if msg.block_status else "unblocked")
        
        # MsgLogoutNotification
        elif isinstance(msg, mc.MsgLogoutNotification):
            self.log.info(f"User logged out by terminal request")

        # MsgChecklistResponses
        elif isinstance(msg, mc.MsgChecklistResponses):
            self.log.info(f"Received {msg.as_dict()}")

        # MsgChecklistVersionNotification
        elif isinstance(msg, mc.MsgChecklistVersionNotification):
            self.log.info(f"Received {msg.as_dict()}")
            if msg.checklist_version != len(self.checklists):
                self.log.info(f"Sending checklist update (current_version={len(self.checklists)}, remote_version={msg.checklist_version})")
                self.send_current_checklist()
            else:
                self.log.info(f"User terminal checklist version is updated (version={msg.checklist_version}. Not sending update.")
        
        # MsgUserQuestionResponse
        elif isinstance(msg, mc.MsgUserQuestionResponse):
            self.log.info(f"Received {msg.as_dict()}")

        # MsgImpactReport
        elif isinstance(msg, mc.MsgImpactReport):
            self.log.info(f"Received {msg.as_dict()}")
        
        else:
            self.log.warning(f"Message of type {type(msg)} unexpected")

    def single_pass(self):
        done_something = False

        # Receive messages from terminal
        try:
            obj = self._mq.get_nowait()
        except queue.Empty:
            pass
        else:
            if 'type' not in obj:
                self.log.error(f"Invalid frame in UserTerminal queue: {obj}")
            if obj['type'] == 'user_received_malformed':
                self.log.error(f"Invalid message received: {obj}")
            elif obj['type'] == 'user_received':
                self.process_msg_from_terminal(obj['msg'])
            elif obj['type'] == 'user_undelivered':
                self.log.warning(f"Unable to deliver message {obj['msg']}. No connection with user terminal")
            else:
                self.log.error(f"Unknown frame type in UserTerminal queue: {obj}")

        self.check_for_keyboard_cmd()

        return done_something

    def loop(self):
        while True:
            if not self.single_pass():
                # If the loop didn't do anything, put a small delay to avoid hogging the processor.
                sleep(0.01)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.ut.terminate()

if __name__ == '__main__':
    try:
        with Main() as main:
            main.loop()
    except KeyboardInterrupt:
        print("interrupted by user")
