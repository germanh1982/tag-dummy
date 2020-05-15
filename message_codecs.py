import field_codecs as fc
from itertools import islice
import json

'''
Message type classes
All these classes can be constructed from one parameter. Depending on it's
type, it's interpreted as one of the following:

str: Interpreted as a JSON string defining the object's contents.
bytes: Interpreted as the binary definition of the object
dict: Interpreted as a dictionary object containing the object's field values.

Also, each one of these classes have at least the methods as_bytes(),
as dict() and as_json() to dump the object's contents as an object of the
corresponding type.
'''

"""
MsgLoginRequest()
[ type(1) | uid(4) | tagid(8) ]
"""
class MsgLoginRequest():
    TYPE = 1
    NAME = 'login_request'

    def __init__(self, value):
        if isinstance(value, str):
            value = json.loads(value)

        if isinstance(value, bytes):
            it = iter(value)
            if next(it) != self.TYPE:
                raise ValueError(self.TYPE)
            self.uid = fc.FieldUID(bytes(islice(it, fc.FieldUID.SIZE)))
            self.tagid = fc.FieldTagID(bytes(islice(it, fc.FieldTagID.SIZE)))
            assert next(it, None) is None, "Raw input length doesn't correspond with this class"
            
        elif isinstance(value, dict):
            if 'type' in value and value['type'] != self.NAME:
                raise ValueError("Packet type unexpected: {value['type']}")
            self.uid = fc.FieldUID(value['uid'])
            self.tagid = fc.FieldTagID(value.get('tagid', None))

        else:
            raise ValueError

    def as_bytes(self):
        out = bytes([self.TYPE])
        out += self.uid.as_bytes()
        out += self.tagid.as_bytes()
        return out

    def as_dict(self):
        return {
            'type': self.NAME,
            'uid': self.uid.value,
            'tagid': self.tagid.value
        }

    def as_json(self):
        return json.dumps(self.dict())

"""
MsgLoginResponse()
[ type(1) | response(1) | uid(4) | username(16) | profile(1) ]
"""
class MsgLoginResponse():
    TYPE = 2
    NAME = 'login_response'

    def __init__(self, value):
        if isinstance(value, str):
            value = json.loads(value)

        if isinstance(value, bytes):
            it = iter(value)
            if next(it) != self.TYPE:
                raise ValueError(self.TYPE)
            self.response = next(it)
            self.uid = fc.FieldUID(bytes(islice(it, fc.FieldUID.SIZE)))
            self.username = fc.FieldUsername(bytes(islice(it, fc.FieldUsername.SIZE)))
            self.profile = next(it)
            assert next(it, None) is None, "Raw input length doesn't correspond with this class"

        elif isinstance(value, dict):
            if 'type' in value and value['type'] != self.NAME:
                raise ValueError("Packet type unexpected: {value['type']}")
            self.response = bool(value['response'])
            self.username = fc.FieldUsername(value.get('username', None))
            self.uid = fc.FieldUID(value.get('uid', None))
            self.profile = int(value['profile'])

        else:
            raise ValueError

    def as_bytes(self):
        out = bytes([self.TYPE])
        out += bytes([self.response])
        out += self.username.as_bytes()
        out += self.uid.as_bytes()
        out += bytes([self.profile])
        return out

    def as_dict(self):
        return {
            'type': self.NAME,
            'response': self.response,
            'username': self.username.value,
            'uid': self.uid.value,
            'profile': self.profile
        }

    def as_json(self):
        return json.dumps(self.as_dict())

"""
MsgLogoutNotification()
[ type(1) | tagid(8) ]
"""
class MsgLogoutNotification():
    TYPE = 3
    NAME = 'logout_notification'

    def __init__(self, value):
        if isinstance(value, str):
            value = json.loads(value)

        if isinstance(value, bytes):
            it = iter(value)
            if next(it) != self.TYPE:
                raise ValueError(self.TYPE)
            self.tagid = fc.FieldTagID(bytes(islice(it, fc.FieldTagID.SIZE)))
            assert next(it, None) is None, "Raw input length doesn't correspond with this class"
            
        elif isinstance(value, dict):
            if 'type' in value and value['type'] != self.NAME:
                raise ValueError("Packet type unexpected: {value['type']}")
            self.tagid = fc.FieldTagID(value.get('tagid', None))

        else:
            raise ValueError

    def as_bytes(self):
        out = bytes([self.TYPE])
        out += self.tagid.as_bytes()
        return out

    def as_dict(self):
        return {
            'type': self.NAME,
            'tagid': self.tagid.value
        }

    def as_json(self):
        return json.dumps(self.as_dict())

"""
MsgChecklistUpdateStart()
[ type(1) | segments(1) | checklist_version(1) | payload_length(2) ]
"""
class MsgChecklistUpdateStart():
    TYPE = 5
    NAME = 'checklist_update_start'

    def __init__(self, value):
        if isinstance(value, str):
            value = json.loads(value)

        if isinstance(value, bytes):
            it = iter(value)
            if next(it) != self.TYPE:
                raise ValueError(self.TYPE)
            self.segments = next(it)
            self.checklist_version = next(it)
            self.length = fc.FieldPayloadLength(bytes(islice(it, fc.FieldPayloadLength.SIZE)))
            assert next(it, None) is None, "Raw input length doesn't correspond with this class"
            
        elif isinstance(value, dict):
            if 'type' in value and value['type'] != self.NAME:
                raise ValueError("Packet type unexpected: {value['type']}")
            self.segments = int(value['segments'])
            self.checklist_version = int(value['checklist_version'])
            self.length = fc.FieldPayloadLength(value['length'])

        else:
            raise ValueError

    def as_bytes(self):
        out = bytes([self.TYPE])
        out += bytes([self.segments])
        out += bytes([self.checklist_version])
        out += self.length.as_bytes()
        return out

    def as_dict(self):
        return {
            'type': self.NAME,
            'segments': self.segments,
            'checklist_version': self.checklist_version,
            'length': self.length.value
        }

    def as_json(self):
        return json.dumps(self.as_dict())
    
"""
MsgChecklistUpdateSegment()
[ type(1) | checklist_version(1) | seq_no(1) | segment(31) ]
"""
class MsgChecklistUpdateSegment():
    TYPE = 6
    NAME = 'checklist_update_segment'

    def __init__(self, value):
        if isinstance(value, str):
            value = json.loads(value)

        if isinstance(value, bytes):
            it = iter(value)
            if next(it) != self.TYPE:
                raise ValueError(self.TYPE)
            self.checklist_version = next(it)
            self.seq_no = next(it)
            self.segment = fc.FieldChecklistSegment(bytes(islice(it, fc.FieldChecklistSegment.SIZE)))
            assert next(it, None) is None, "Raw input length doesn't correspond with this class"
            
        elif isinstance(value, dict):
            if 'type' in value and value['type'] != self.NAME:
                raise ValueError("Packet type unexpected: {value['type']}")
            self.checklist_version = int(value['checklist_version'])
            self.seq_no = int(value['seq_no'])
            self.segment = fc.FieldChecklistSegment(value['segment'])

        else:
            raise ValueError

    def as_bytes(self):
        out = bytes([self.TYPE])
        out += bytes([self.checklist_version])
        out += bytes([self.seq_no])
        out += self.segment.as_bytes()
        return out

    def as_dict(self):
        return {
            'type': self.NAME,
            'checklist_version': self.checklist_version,
            'seq_no': self.seq_no,
            'segment': self.segment.value
        }

    def as_json(self):
        return json.dumps(self.as_dict())
    
"""
MsgChecklistUpdate()
[ type(1) | checklist_version(1) | checklist_data(4096) ]
"""
class MsgChecklistUpdate():
    TYPE = 7
    NAME = 'checklist_update'

    def __init__(self, value):
        if isinstance(value, str):
            value = json.loads(value)

        if isinstance(value, bytes):
            it = iter(value)
            if next(it) != self.TYPE:
                raise ValueError(self.TYPE)
            self.checklist_data = fc.FieldChecklistdData(bytes(islice(it, fc.FieldChecklistData.SIZE)))
            assert next(it, None) is None, "Raw input length doesn't correspond with this class"
            
        elif isinstance(value, dict):
            if 'type' in value and value['type'] != self.NAME:
                raise ValueError("Packet type unexpected: {value['type']}")
            self.checklist_version = int(value['checklist_version'])
            self.checklist_data = fc.FieldChecklistData(value['checklist_data'])

        else:
            raise ValueError

    def as_bytes(self):
        out = bytes([self.TYPE])
        out += bytes([self.checklist_version])
        out += self.checklist_data.as_bytes()
        return out

    def as_dict(self):
        return {
            'type': self.NAME,
            'checklist_version': self.checklist_version,
            'checklist_data': self.checklist_data.value
        }

    def as_json(self):
        return json.dumps(self.as_dict())
    
"""
MsgChecklistResponses()
[ type(1) | tagid(8) | responses(20) | checklist_version(1) ]
"""
class MsgChecklistResponses():
    TYPE = 8
    NAME = 'checklist_responses'

    def __init__(self, value):
        if isinstance(value, str):
            value = json.loads(value)

        if isinstance(value, bytes):
            it = iter(value)
            if next(it) != self.TYPE:
                raise ValueError(self.TYPE)
            self.tagid = fc.FieldTagID(bytes(islice(it, fc.FieldTagID.SIZE)))
            self.responses = fc.FieldChecklistResponses(bytes(islice(it, fc.FieldChecklistResponses.SIZE)))
            self.checklist_version = next(it)
            assert next(it, None) is None, "Raw input length doesn't correspond with this class"

        elif isinstance(value, dict):
            if 'type' in value and value['type'] != self.NAME:
                raise ValueError("Packet type unexpected: {value['type']}")
            self.tagid = fc.FieldTagID(value.get('tagid', None))
            self.responses = fc.FieldChecklistResponses(value['responses'])
            self.checklist_version = int(value['checklist_version'])

        else:
            raise ValueError

    def as_bytes(self):
        out = bytes([self.TYPE])
        out += self.tagid.as_bytes()
        out += self.responses.as_bytes()
        out += bytes([self.checklist_version])
        return out

    def as_dict(self):
        return {
            'type': self.NAME,
            'tagid': self.tagid.value,
            'responses': self.responses.value,
            'checklist_version': self.checklist_version
        }

    def as_json(self):
        return json.dumps(self.as_dict())
    
"""
MsgChecklistVersionNotification()
[ type(1) | checklist_version(1) ]
"""
class MsgChecklistVersionNotification():
    TYPE = 10
    NAME = 'checklist_version_notification'

    def __init__(self, value):
        if isinstance(value, str):
            value = json.loads(value)

        if isinstance(value, bytes):
            it = iter(value)
            if next(it) != self.TYPE:
                raise ValueError(self.TYPE)
            self.checklist_version = next(it)
            assert next(it, None) is None, "Raw input length doesn't correspond with this class"
            
        elif isinstance(value, dict):
            if 'type' in value and value['type'] != self.NAME:
                raise ValueError("Packet type unexpected: {value['type']}")
            self.checklist_version = int(value['checklist_version'])

        else:
            raise ValueError

    def as_bytes(self):
        out = bytes([self.TYPE])
        out += bytes([self.checklist_version])
        return out

    def as_dict(self):
        return {
            'type': self.NAME,
            'checklist_version': self.checklist_version
        }

    def as_json(self):
        return json.dumps(self.as_dict())
    
"""
MsgUserQuestionStart()
[ type(1) | question_id(1) | segments(1) | payload_length(2) ]
"""
class MsgUserQuestionStart():
    TYPE = 11
    NAME = 'user_question_start'

    def __init__(self, value):
        if isinstance(value, str):
            value = json.loads(value)

        if isinstance(value, bytes):
            it = iter(value)
            if next(it) != self.TYPE:
                raise ValueError(self.TYPE)
            self.question_id = next(it)
            self.segments = next(it)
            self.length = fc.FieldPayloadLength(bytes(islice(it, fc.FieldPayloadLength.SIZE)))
            assert next(it, None) is None, "Raw input length doesn't correspond with this class"
            
        elif isinstance(value, dict):
            if 'type' in value and value['type'] != self.NAME:
                raise ValueError("Packet type unexpected: {value['type']}")
            self.question_id = int(value['question_id'])
            self.segments = int(value['segments'])
            self.length = fc.FieldPayloadLength(value['length'])

        else:
            raise ValueError
 
    def as_bytes(self):
        out = bytes([self.TYPE])
        out += bytes([self.question_id])
        out += bytes([self.segments])
        out += self.length.as_bytes()
        return out

    def as_dict(self):
        return {
            'type': self.NAME,
            'question_id': self.question_id,
            'segments': self.segments,
            'length': self.length.value
        }

    def as_json(self):
        return json.dumps(self.as_dict())
    
"""
MsgUserQuestionSegment()
[ type(1) | question_id(1) | seq_no(1) | data(31) ]
"""
class MsgUserQuestionSegment():
    TYPE = 12
    NAME = 'user_question_segment'
    DATA_LENGTH = 30

    def __init__(self, value):
        if isinstance(value, str):
            value = json.loads(value)

        if isinstance(value, bytes):
            it = iter(value)
            if next(it) != self.TYPE:
                raise ValueError(self.TYPE)
            self.question_id = next(it)
            self.seq_no = next(it)
            self.data = fc.FieldUserQuestionData(bytes(islice(it, fc.FieldUserQuestionData.SIZE)))
            assert next(it, None) is None, "Raw input length doesn't correspond with this class"
            
        elif isinstance(value, dict):
            if 'type' in value and value['type'] != self.NAME:
                raise ValueError("Packet type unexpected: {value['type']}")
            self.question_id = int(value['question_id'])
            self.seq_no = int(value['seq_no'])
            self.data = fc.FieldUserQuestionData(value['data'])

        else:
            raise ValueError
 
    def as_bytes(self):
        out = bytes([self.TYPE])
        out += bytes([self.question_id])
        out += bytes([self.seq_no])
        out += self.data.as_bytes()
        return out

    def as_dict(self):
        return {
            'type': self.NAME,
            'question_id': self.question_id,
            'seq_no': self.seq_no,
            'data': self.data.value
        }

    def as_json(self):
        return json.dumps(self.as_dict())
    
"""
MsgUserQuestion()
[ type(1) | question_id(1) | user_question(...) ]
"""
class MsgUserQuestion():
    TYPE = 13
    NAME = 'user_question'

    def __init__(self, value):
        if isinstance(value, str):
            value = json.loads(value)

        if isinstance(value, bytes):
            it = iter(value)
            if next(it) != self.TYPE:
                raise ValueError(self.TYPE)
            self.question_id = next(it)
            self.user_question = fc.FieldUserQuestion(bytes(islice(it, fc.FieldUserQuestion.SIZE)))
            assert next(it, None) is None, "Raw input length doesn't correspond with this class"
            
        elif isinstance(value, dict):
            if 'type' in value and value['type'] != self.NAME:
                raise ValueError("Packet type unexpected: {value['type']}")
            self.question_id = int(value['question_id'])
            self.user_question = fc.FieldUserQuestion(value['user_question'])

        else:
            raise ValueError

    def as_bytes(self):
        out = bytes([self.TYPE])
        out += bytes([self.question_id])
        out += self.user_question.as_bytes()
        return out

    def as_dict(self):
        return {
            'type': self.NAME,
            'question_id': self.question_id,
            'user_question': self.user_question.value
        }

    def as_json(self):
        return json.dumps(self.as_dict())
    
"""
MsgUserQuestionResponse()
[ type(1) | tagid(8) | question_id(1) | response(1) ]
"""
class MsgUserQuestionResponse():
    TYPE = 14
    NAME = 'user_question_response'

    def __init__(self, value):
        if isinstance(value, str):
            value = json.loads(value)

        if isinstance(value, bytes):
            it = iter(value)
            if next(it) != self.TYPE:
                raise ValueError(self.TYPE)
            self.tagid = fc.FieldTagID(bytes(islice(it, fc.FieldTagID.SIZE)))
            self.question_id = next(it)
            self.responses = fc.FieldUserQuestionResponse(next(it))
            assert next(it, None) is None, "Raw input length doesn't correspond with this class"
            
        elif isinstance(value, dict):
            if 'type' in value and value['type'] != self.NAME:
                raise ValueError("Packet type unexpected: {value['type']}")
            self.tagid = fc.FieldTagID(value.get('tagid', None))
            self.question_id = int(value['question_id'])
            self.responses = fc.FieldUserQuestionResponse(value['responses'])

        else:
            raise ValueError

    def as_bytes(self):
        out = bytes([self.TYPE])
        out += self.tagid.as_bytes()
        out += bytes([self.question_id])
        out += self.responses.as_bytes()
        return out

    def as_dict(self):
        return {
            'type': self.NAME,
            'tagid': self.tagid.value,
            'question_id': self.question_id,
            'responses': self.responses.value
        }

    def as_json(self):
        return json.dumps(self.as_dict())
    
"""
MsgImpactReport()
[ type(1) | tagid(8) | severity(1) | accel_direction(1) ]
"""
class MsgImpactReport():
    TYPE = 15
    NAME = 'impact_report'

    def __init__(self, value):
        if isinstance(value, str):
            value = json.loads(value)

        if isinstance(value, bytes):
            it = iter(value)
            if next(it) != self.TYPE:
                raise ValueError(self.TYPE)
            self.tagid = fc.FieldTagID(bytes(islice(it, fc.FieldTagID.SIZE)))
            self.severity = next(it)
            self.accel_direction = next(it)
            assert next(it, None) is None, "Raw input length doesn't correspond with this class"
            
        elif isinstance(value, dict):
            if 'type' in value and value['type'] != self.NAME:
                raise ValueError("Packet type unexpected: {value['type']}")
            self.tagid = fc.FieldTagID(value.get('tagid', None))
            self.severity = int(value['severity'])
            self.accel_direction = int(value['accel_direction'])

        else:
            raise ValueError

    def as_bytes(self):
        out = bytes([self.TYPE])
        out += self.tagid.as_bytes()
        out += bytes([self.severity])
        out += bytes([accel_direction])
        return out

    def as_dict(self):
        return {
            'type': self.NAME,
            'tagid': self.tagid.value,
            'severity': self.severity,
            'accel_direction': self.accel_direction
        }

    def as_json(self):
        return json.dumps(self.as_dict())
    
"""
MsgVehicleReport()
[ type(1) | tagid(8) | frame_counter(2) | uwbpos | gpspos ]
"""
class MsgVehicleReport():
    TYPE = 16
    NAME = 'vehicle_report'

    def __init__(self, value):
        if isinstance(value, str):
            value = json.loads(value)

        if isinstance(value, bytes):
            it = iter(value)
            if next(it) != self.TYPE:
                raise ValueError(self.TYPE)
            self.tagid = fc.FieldTagID(bytes(islice(it, fc.FieldTagID.SIZE)))
            self.frame_counter = fc.FieldFrameCounter(bytes(islice(it, fc.FieldFrameCounter.SIZE)))
            self.uwbpos = fc.FieldUWBPosition(bytes(islice(it, fc.FieldUWBPosition.SIZE)))
            self.gpspos = fc.FieldGPSPosition(bytes(islice(it, fc.FieldGPSPosition.SIZE)))
            assert next(it, None) is None, "Raw input length doesn't correspond with this class"
            
        elif isinstance(value, dict):
            if 'type' in value and value['type'] != self.NAME:
                raise ValueError("Packet type unexpected: {value['type']}")
            self.tagid = fc.FieldTagID(value.get('tagid', None))
            self.frame_counter = fc.FieldFrameCounter(value['frame_counter'])
            self.uwbpos = fc.FieldUWBPosition(value['uwbpos'])
            self.gpspos = fc.FieldGPSPosition(value['gpspos'])

        else:
            raise ValueError

    def as_bytes(self):
        out = bytes([self.TYPE])
        out += self.tagid.as_bytes()
        out += self.frame_counter.as_bytes()
        out += self.uwbpos.as_bytes()
        out += self.gpspos.as_bytes()
        return out

    def as_dict(self):
        return {
            'type': self.NAME,
            'tagid': self.tagid.value,
            'frame_counter': self.frame_counter.value,
            'uwbpos': self.uwbpos.value,
            'gpspos': self.gpspos.value
        }

    def as_json(self):
        return json.dumps(self.as_dict())
    
"""
MsgSetBlockStatus()
[ type(1) | tagid(8) | block_status(1) ]
"""
class MsgSetBlockStatus():
    TYPE = 17
    NAME = 'set_block_status'

    def __init__(self, value):
        if isinstance(value, str):
            value = json.loads(value)

        if isinstance(value, bytes):
            it = iter(value)
            if next(it) != self.TYPE:
                raise ValueError(self.TYPE)
            self.tagid = fc.FieldTagID(bytes(islice(it, fc.FieldTagID.SIZE)))
            self.block_status = bool(next(it))
            assert next(it, None) is None, "Raw input length doesn't correspond with this class"
            
        elif isinstance(value, dict):
            if 'type' in value and value['type'] != self.NAME:
                raise ValueError("Packet type unexpected: {value['type']}")
            self.tagid = fc.FieldTagID(value.get('tagid', None))
            self.block_status = bool(value['block_status'])

        else:
            raise ValueError

    def as_bytes(self):
        out = bytes([self.TYPE])
        out += self.tagid.as_bytes()
        out += bytes([self.block_status])
        return out

    def as_dict(self):
        return {
            'type': self.NAME,
            'tagid': self.tagid.value,
            'block_status': self.block_status
        }

    def as_json(self):
        return json.dumps(self.as_dict())
    
"""
MsgTimeRequest()
[ type(1) | tagid(8) ]
"""
class MsgTimeRequest():
    TYPE = 18
    NAME = 'time_request'

    def __init__(self, value):
        if isinstance(value, str):
            value = json.loads(value)

        if isinstance(value, bytes):
            it = iter(value)
            if next(it) != self.TYPE:
                raise ValueError(self.TYPE)
            self.tagid = fc.FieldTagID(bytes(islice(it, fc.FieldTagID.SIZE)))
            assert next(it, None) is None, "Raw input length doesn't correspond with this class"
            
        elif isinstance(value, dict):
            if 'type' in value and value['type'] != self.NAME:
                raise ValueError("Packet type unexpected: {value['type']}")
            self.tagid = fc.FieldTagID(value.get('tagid', None))

        else:
            raise ValueError

    def as_bytes(self):
        out = bytes([self.TYPE])
        out += self.tagid.as_bytes()
        return out

    def as_dict(self):
        return {
            'type': self.NAME,
            'tagid': self.tagid.value
        }

    def as_json(self):
        return json.dumps(self.as_dict())
    
"""
MsgTimeSet()
[ type(1) | timestamp(4) ]
"""
class MsgTimeSet():
    TYPE = 19 
    NAME = 'time_set'

    def __init__(self, value):
        if isinstance(value, str):
            value = json.loads(value)

        if isinstance(value, bytes):
            it = iter(value)
            if next(it) != self.TYPE:
                raise ValueError(self.TYPE)
            self.timestamp = fc.FieldTimestamp(bytes(islice(it, fc.FieldTimestamp.SIZE)))
            assert next(it, None) is None, "Raw input length doesn't correspond with this class"
            
        elif isinstance(value, dict):
            if 'type' in value and value['type'] != self.NAME:
                raise ValueError("Packet type unexpected: {value['type']}")
            self.timestamp = fc.FieldTimestamp(value['timestamp'])

        else:
            raise ValueError

    def as_bytes(self):
        out = bytes([self.TYPE])
        out += self.timestamp.as_bytes()
        return out

    def as_dict(self):
        return {
            'type': self.NAME,
            'timestamp': self.timestamp.value
        }

    def as_json(self):
        return json.dumps(self.as_dict())
  
"""
MsgTagConfig()
[ type(1) | sensitivity(1) | update_rate(1) | vehicle_name(16) ]
"""
class MsgTagConfig():
    TYPE = 20
    NAME = 'tag_config'

    def __init__(self, value):
        if isinstance(value, bytes):
            it = iter(value)
            if next(it) != self.TYPE:
                raise ValueError(self.TYPE)
            self.crash_sens = int(next(it))
            self.report_rate = int(next(it))
            self.vehicle_name = fc.FieldVehicleName(bytes(islice(it, fc.FieldVehicleName.SIZE)))
            assert next(it, None) is None, "Raw input length doesn't correspond with this class"

        elif isinstance(value, dict):
            if 'type' in value and value['type'] != self.NAME:
                raise ValueError("Packet type unexpected: {value['type']}")
            self.crash_sens = int(value['crash_sens'])
            self.report_rate = int(value['report_rate'])
            self.vehicle_name = fc.FieldVehicleName(value['vehicle_name'])

        else:
            raise ValueError

    def as_bytes(self):
        out = bytes([self.TYPE])
        out += bytes([self.crash_sens])
        out += bytes([self.report_rate])
        out += self.vehicle_name.as_bytes()
        return out

    def as_dict(self):
        return {
            'crash_sens': self.crash_sens,
            'report_rate': self.report_rate,
            'vehicle_name': self.vehicle_name.value
        }

    def as_json(self):
        return json.dumps(self.as_dict())

def parse_dict(msg):
    if msg['type'] == MsgLoginRequest.NAME:
        return MsgLoginRequest(msg)
    elif msg['type'] == MsgLoginResponse.NAME:
        return MsgLoginResponse(msg)
    elif msg['type'] == MsgLogoutNotification.NAME:
        return MsgLogoutNotification(msg)
    elif msg['type'] == MsgChecklistUpdateStart.NAME:
        return MsgChecklistUpdateStart(msg)
    elif msg['type'] == MsgChecklistUpdateSegment.NAME:
        return MsgChecklistUpdateSegment(msg)
    elif msg['type'] == MsgChecklistUpdate.NAME:
        return MsgChecklistUpdate(msg)
    elif msg['type'] == MsgChecklistResponses.NAME:
        return MsgChecklistResponses(msg)
    elif msg['type'] == MsgChecklistVersionNotification.NAME:
        return MsgChecklistVersionNotification(msg)
    elif msg['type'] == MsgUserQuestionStart.NAME:
        return MsgUserQuestionStart(msg)
    elif msg['type'] == MsgUserQuestionSegment.NAME:
        return MsgUserQuestionSegment(msg)
    elif msg['type'] == MsgUserQuestion.NAME:
        return MsgUserQuestion(msg)
    elif msg['type'] == MsgUserQuestionResponse.NAME:
        return MsgUserQuestionResponse(msg)
    elif msg['type'] == MsgImpactReport.NAME:
        return MsgImpactReport(msg)
    elif msg['type'] == MsgVehicleReport.NAME:
        return MsgVehicleReport(msg)
    elif msg['type'] == MsgTagConfig.NAME:
        return MsgTagConfig(msg)
    elif msg['type'] == MsgSetBlockStatus.NAME:
        return MsgSetBlockStatus(msg)
    elif msg['type'] == MsgTimeRequest.NAME:
        return MsgTimeRequest(msg)
    elif msg['type'] == MsgTimeSet.NAME:
        return MsgTimeSet(msg)
    else:
        raise Exception(f"Message couldn't be parsed: {msg}")

def parse_bytes(msg):
    typecode_to_msg = {
        MsgLoginRequest.TYPE: MsgLoginRequest,
        MsgLoginResponse.TYPE: MsgLoginResponse,
        MsgLogoutNotification.TYPE: MsgLogoutNotification,
        MsgChecklistUpdateStart.TYPE: MsgChecklistUpdateStart,
        MsgChecklistUpdateSegment.TYPE: MsgChecklistUpdateSegment,
        MsgChecklistResponses.TYPE: MsgChecklistResponses,
        MsgChecklistVersionNotification.TYPE: MsgChecklistVersionNotification,
        MsgUserQuestionStart.TYPE: MsgUserQuestionStart,
        MsgUserQuestionSegment.TYPE: MsgUserQuestionSegment,
        MsgUserQuestionResponse.TYPE: MsgUserQuestionResponse,
        MsgImpactReport.TYPE: MsgImpactReport,
        MsgVehicleReport.TYPE: MsgVehicleReport,
        MsgTagConfig.TYPE: MsgTagConfig,
        MsgSetBlockStatus.TYPE: MsgSetBlockStatus,
        MsgTimeRequest.TYPE: MsgTimeRequest,
        MsgTimeSet.TYPE: MsgTimeSet
    }
    return typecode_to_msg[msg[0]](msg)

def parse_json(msg):
    return parse_dict(json.loads(msg))

"""
Grabs the full checklist_data as a string, generates the MsgChecklistUpdateStart header message and the MsgChecklistUpdateSegment messages
"""
def checklist_splitter(checklist_data, checklist_version):
    segments = []
    databytes = json.dumps(checklist_data).encode()
    it = iter(databytes)
    while True:
        segment = bytes(islice(it, fc.FieldChecklistSegment.SIZE))
        if len(segment) < fc.FieldChecklistSegment.SIZE:
            segment += b'\0' * (fc.FieldChecklistSegment.SIZE - len(segment))
            segments.append(segment)
            break
        else:
            segments.append(segment)

    output = []
    output.append(MsgChecklistUpdateStart({'segments': len(segments), 'checklist_version': checklist_version, 'length': len(databytes)}))
    for seq_no, segment in enumerate(segments):
        output.append(MsgChecklistUpdateSegment({'checklist_version': checklist_version, 'seq_no': seq_no, 'segment': segment}))
    return output

"""
Grabs a complete user question payload as string, and generates header and segment messages to be transmitted via the comms link
"""
def user_question_splitter(user_question_data, question_id):
    segments = []
    databytes = json.dumps(user_question_data).encode()
    it = iter(databytes)
    while True:
        segment = islice(it, fc.FieldUserQuestionSegment.SIZE)
        if len(segment) < fc.FieldUserQuestionSegment.SIZE:
            segment += b'\0' * (fc.FieldUserQuestionSegment.SIZE - len(segment))
            segments.append(segment)
            break
        else:
            segments.append(segment)

    output = []
    output.append(MsgUserQuestionStart({'segments': len(segments), 'question_id': question_id, 'length': len(databytes)}))
    for seq_no, segment in enumerate(segments):
        output.append(MsgUserQuestionSegment({'question_id': question_id, 'seq_no': seq_no, 'data': segment}))
    return output
