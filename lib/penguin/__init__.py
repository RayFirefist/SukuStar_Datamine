import os
import struct
import json

CONST_KEYS = [
    0x5595f498,
    0x15e7ee5,
    0x7ef3eac1
]

class FileStream:

    def __init__(self, file):
        self.position = 0
        self.littleEndian = True
        if not type(file) == bytes:
            self.f = open(file, "rb")
            if self.f == False:
                raise Exception("Unable to open %s" % file)
            self.data = self.f.read()
        else:
            self.data = file
        self.size = self.data.__len__()

    def __del__(self):
        try:
            self.f.close()
        except AttributeError:
            pass

    def read(self, length:int):
        # print(self.position, length)
        data = self.data[self.position:self.position+length]
        # print(data)
        self.position += length
        if self.littleEndian:
            try:
                return struct.unpack("<Q", data)
            except struct.error:
                return data
        else:
            return data

    def readString(self):
        length = self.readByte()
        return self.read(length)

    def readInt(self):
        value = self.readByte()
        if value > 128:
            b2 = self.readByte()
            b3 = self.readByte()
            b4 = self.readByte()
            value = value + ((b2 + ((b3 + (b4 << 8)) << 8)) << 7)
            pass
        return value
    
    def readByte(self):
        return int.from_bytes(self.read(1), byteorder="little" if self.littleEndian else "big", signed=False)

pass

def decrypt_stream(data:bytes, key0:int, key1:int, key2:int, isAssets:bool = False):
    if isAssets == False:
        key0 = key0 ^ CONST_KEYS[0]
        key1 = key1 ^ CONST_KEYS[1]
        key2 = key2 ^ CONST_KEYS[2]
    countView=5
    out=bytearray()
    for position in range(0, data.__len__()):
        temp = int.from_bytes(data[position:position+1], byteorder="big") ^ (((key1 ^ key0 ^ key2) >> 24) & 0xff)
        key0 = (0x343FD * key0 + 0x269EC3) & 0xFFFFFFFF
        key1 = (0x343FD * key1 + 0x269EC3) & 0xFFFFFFFF
        key2 = (0x343FD * key2 + 0x269EC3) & 0xFFFFFFFF
        if countView < 5:
            countView+=1
            print(str(temp).encode("utf-8"))
        out.append(temp)
        pass
    return out

def getKeyData(k:str):
    keys=[]
    for x in range(0, k.__len__()):
        if x % 8 > 0:
            continue
        # print("KEY %s" % k[x:x+8])
        keys.append(int(k[x:x+8].decode("utf8"), 16))
    return keys

def masterDataRead(file:FileStream):
    file.position = 20
    hash = file.readString()
    lang = file.readString()
    rows = file.readInt()

    # print(hash, lang, rows)

    out = []
    for x in range(0, rows):
        v15 = file.readString() # db name
        v16 = file.readString() # db keys
        out.append(
            {
                "db_name": v15.decode('utf8'),
                "db_keys": v16.decode('utf8'),
                "db_keys_list": getKeyData(v16),
                "sha1": "",
                "size": 0
            }
        )
    for x in range(0, rows):
        v15 = file.readString() # sha1 db
        v16 = file.readString() # size db
        out[x]['sha1'] = hex(int.from_bytes(file.read(20), byteorder="big"))
        out[x]['size'] = file.readInt()

    return out


if __name__ == "__main__":
    file = FileStream("./masterdata_i_ja")
    print(json.dumps(masterDataRead(file)))
    pass