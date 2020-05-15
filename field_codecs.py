from itertools import islice
import datetime as dt
import json

ENDIANNESS = 'little'

"""
FieldInteger(): Generic class from which all signed integer types derive.
"""
class FieldInteger():
    def __init__(self, value, length):
        self._length = length
        self.value = value

    @property
    def value(self):
        return self._value
        
    @value.setter
    def value(self, value):
        if isinstance(value, int):
            self._value = value

        elif isinstance(value, bytes):
            if len(value) != self._length:
                raise ValueError
            self._value = int.from_bytes(value, ENDIANNESS)
        
        elif value is None:
            self._value = None
        
        else:
            raise ValueError

    def as_bytes(self):
        return self._value.to_bytes(self._length, ENDIANNESS)

"""
FieldText(): Generic class from which all text-based classes derive.
"""
class FieldText():
    def __init__(self, value, length):
        self._length = length
        self.value = value

    @property
    def value(self):
        return self._value
        
    @value.setter
    def value(self, value):
        if isinstance(value, str):
            if len(value.encode()) > self._length:
                raise ValueError
            self._value = value

        elif isinstance(value, bytes):
            if len(value) > self._length:
                raise ValueError
            t = bytes(value).decode()
            p = t.index('\0')
            self._value = t if p == -1 else t[0:p]

        elif value is None:
            self._value = None

        else:
            raise ValueError

    def as_bytes(self):
        return (self._value.encode() + b'\0' * self._length)[:self._length]

"""
FieldBinary(): Generic class from which all binary processing classes derive.
When constructing from a binary string, the parameter value must be a type list(), to distinguish it from the raw (bytes) value.
The value cannot be read as a class cast, because bytes(
"""
class FieldBinary():
    def __init__(self, value, length):
        self._length = length
        self.value = value
    
    @property
    def value(self):
        return self._value
     
    @value.setter
    def value(self, value):
        if isinstance(value, list):
            if len(value) != self._length:
                raise ValueError
            self._value = bytes(value)

        elif isinstance(value, bytes):
            if len(value) != self._length:
                raise ValueError
            self._value = value

        elif isinstance(value, str):
            if len(value) > self._length:
                raise ValueError
            self._value = value.encode()

        elif value is None:
            self._value = None

        else:
            raise ValueError

    def as_bytes(self):
        return self._value

class FieldJSON():
    def __init__(self, value, length):
        self._length = length
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if isinstance(value, bytes):
            if len(value) != self._length:
                raise ValueError
            strvalue = bytes(value).decode()
            try:
                i = strvalue.index('\0')
            except ValueError:
                pass
            else:
                strvalue = strvalue[0:i]

            self._value = json.loads(strvalue)

        else:
            strvalue = json.dumps(value)
            if len(strvalue.encode()) > self._length:
                raise ValueError
            self._value = value

    def as_bytes(self):
        return ((json.dumps(self._value) + '\0' * self._length)[0:self._length]).encode()

class FieldVarLenList():
    def __init__(self, value, length):
        self._length = length
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if isinstance(value, bytes):
            if len(value) != self._length:
                raise ValueError
            self._value = [bool(x) for x in value[1:value[0] + 1]]

        elif isinstance(value, list):
            if len(value) > self._length - 1:
                raise ValueError(value)
            self._value = value

    def as_bytes(self):
        out = bytes([len(self._value)])
        out += bytes(self._value)
        out += bytes(20)
        out = out[:self._length]
        return out

"""
FieldChecklistResponses()
"""
class FieldChecklistResponses():
    NUM_RESPONSES = 5   # 0 < NUM_RESPONSES < 26 (taking packet size of 34 bytes)
    SIZE = NUM_RESPONSES

    def __init__(self, value):
        # This length checking works both for dictionaries and byte strings
        if len(value) != self.NUM_RESPONSES:
            raise ValueError("Message has an incorrect {} number of responses".format(len(value['responses'])))
        if isinstance(value, dict):
            self._value = {}
            for k, v in value.items():
                if v not in (0, 1, 2):
                    raise ValueError
                self._value[int(k)] = v
        elif isinstance(value, bytes):
            for x in value:
                k = x & 0x1f    # The 5 LSB bytes are the question_id
                v = x >> 5 & 0x7    # The 3 MSB bits are the answer value
                self._value[k] = v
        else:
            raise ValueError

    @property
    def value(self):
        return self._value

    def as_bytes(self):
        out = bytes(self.NUM_RESPONSES)
        for k, v in self._value.items():
            out += v << 5 | k
        return out

"""
FieldUID(): Class for parsing and retrieval of 32-bit UIDs.
"""
class FieldUID(FieldInteger):
    SIZE = 4

    def __init__(self, value):
        super().__init__(value, self.SIZE)

"""
FieldTagID(): Class for parsing and retrieval of 64-bit Tag IDs.
"""
class FieldTagID(FieldInteger):
    SIZE = 8

    def __init__(self, value):
        super().__init__(value, self.SIZE)

"""
FieldUsername(): Class for storing fixed-length usernames.
"""
class FieldUsername(FieldText):
    SIZE = 16

    def __init__(self, value):
        super().__init__(value, self.SIZE)

"""
FieldPayloadLength(): Class for storage of payload length variables.
"""
class FieldPayloadLength(FieldInteger):
    SIZE = 2

    def __init__(self, value):
        super().__init__(value, self.SIZE)

"""
FieldUserQuestion(): Stores reconstructed user question data.
"""
class FieldUserQuestion(FieldJSON):
    SIZE = 4096

    def __init__(self, value):
        super().__init__(value, self.SIZE)

"""
FieldUserQuestionSegment(): Stores user question data segment.
"""
class FieldUserQuestionSegment(FieldBinary):
    SIZE = 31

    def __init__(self, value):
        super().__init__(value, self.SIZE)

"""
FieldChecklistData(): Class for storing checklist update (reconstructed).
"""
class FieldChecklistData(FieldJSON):
    SIZE = 4096

    def __init__(self, value):
        super().__init__(value, self.SIZE)

"""
FieldChecklistSegment(): Class for storing checklist update data segments.
"""
class FieldChecklistSegment(FieldBinary):
    SIZE = 31

    def __init__(self, value):
        super().__init__(value, self.SIZE)

"""
FieldUWBPosition(): Composite class for storing XYZ position coordinates and a precision factor.
value = { xpos, ypos, zpos, qf }
raw = [ xpos(3) | ypos(3) | zpos(3) | qf(1) ]
"""
class FieldUWBPosition():
    BYTES_PER_DIM = 3
    SIZE = 3 * BYTES_PER_DIM # The '3' is number of dimensions, the final '1' is for the precision
    CONV_FACTOR = 1e3

    def __init__(self, value):
        self.value = value

    @property
    def value(self):
        return {
            'xpos': self._xpos,
            'ypos': self._ypos,
            'zpos': self._zpos
        }

    @value.setter
    def value(self, value):
        if isinstance(value, dict):
            self._xpos = value['xpos']
            self._ypos = value['ypos']
            self._zpos = value['zpos']

        elif isinstance(value, bytes):
            if len(value) > self.SIZE:
                raise ValueError
            it = iter(value)
            self._xpos = int.from_bytes(islice(it, self.BYTES_PER_DIM), ENDIANNESS, signed=True) / self.CONV_FACTOR
            self._ypos = int.from_bytes(islice(it, self.BYTES_PER_DIM), ENDIANNESS, signed=True) / self.CONV_FACTOR
            self._zpos = int.from_bytes(islice(it, self.BYTES_PER_DIM), ENDIANNESS, signed=True) / self.CONV_FACTOR

        else:
            raise ValueError

    def as_bytes(self):
        out = (self._xpos * self.CONV_FACTOR).to_bytes(self.BYTES_PER_DIM, ENDIANNESS, signed=True)
        out += (self._ypos * self.CONV_FACTOR).to_bytes(self.BYTES_PER_DIM, ENDIANNESS, signed=True)
        out += (self._zpos * self.CONV_FACTOR).to_bytes(self.BYTES_PER_DIM, ENDIANNESS, signed=True)
        return out

"""
FieldGPSPosition(): Composite class for storing lat,lon coordinates along with a precision indicator.
value = { lat, lon, dop }
raw = [ lat(4) | lon(4) | dop(1) ]
The sign of the coordinate fields indicate hemisphere: + = North/East, - = South/West
"""
class FieldGPSPosition():
    BYTES_PER_COORD = 4
    SIZE = 2 * BYTES_PER_COORD 
    CONV_FACTOR = 1e7

    def __init__(self, value):
        self.value = value

    @property
    def value(self):
        return {
            'lat': self._lat,
            'lon': self._lon
        }

    @value.setter
    def value(self, value):
        if isinstance(value, dict):
            self._lat = value['lat']
            self._lon = value['lon']

        elif isinstance(value, bytes):
            if len(value) > self.SIZE:
                raise ValueError
            it = iter(value)
            self._lat = int.from_bytes(islice(it, self.BYTES_PER_COORD), ENDIANNESS, signed=True) / self.CONV_FACTOR
            self._lon = int.from_bytes(islice(it, self.BYTES_PER_COORD), ENDIANNESS, signed=True) / self.CONV_FACTOR

        else:
            raise ValueError

    def as_bytes(self):
        out = int(self._lat * self.CONV_FACTOR).to_bytes(self.BYTES_PER_COORD, ENDIANNESS, signed=True)
        out += int(self._lon * self.CONV_FACTOR).to_bytes(self.BYTES_PER_COORD, ENDIANNESS, signed=True)
        return out

"""
FieldFrameCounter(): Class for storage of Frame Counter fields.
"""
class FieldFrameCounter(FieldInteger):
    SIZE = 2

    def __init__(self, value):
        super().__init__(value, self.SIZE)

"""
FieldTimestamp(): Class for storage of Timestamp values (used in TIME_REQUEST and TIME_SET
"""
class FieldTimestamp(FieldInteger):
    SIZE = 4

    def __init__(self, value):
        super().__init__(value, self.SIZE)

    @property
    def datetime(self):
        return dt.datetime.fromtimestamp(self.value)

    def as_str(self):
        return dt.datetime.fromtimestamp(self.value).strftime('%c')

"""
FieldVehicleName(): Storage and transfer of vehicle name
"""
class FieldVehicleName(FieldText):
    SIZE = 16

    def __init__(self, value):
        super().__init__(value, self.SIZE)

"""
FieldUserQuestionResponse(): Storage and translation of a bool list with variable length
"""
class FieldUserQuestionResponse(FieldVarLenList):
    SIZE = 10

    def __init__(self, value):
        super().__init__(value, self.SIZE)
