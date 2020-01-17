# NovelKit ADV scripts parsers
# Thanks Triangle for demo script

# @(#)All Stars ADV script decompressor
# @(#)Copyright 2020, t
# https://github.com/summertriangle-dev/arposandra/blob/master/LICENSE.md

import sys
import json
import struct
from collections import namedtuple

# Some important defined constants
__all__ = ["load_script", "adv_script_t"]
kADVHeaderLength         = 0x1b                  # 0?
kADVMagic                = 0x80                  # 0x28
kADVHasCompressionMask   = 0x80                  # 0x29
kADVHasResSegMask        = 0x40                  # 0x2A

kADVCTagLength           = 3
kADVCTagSignal           = 0x80

adv_header_t = namedtuple("adv_header_t", (
    "magic",            # [1] kADVMagic.
    "data_flags",       # [1] Bitmask. Has kADVHasResSegMask if there is a
                        #   resource segment, and kADVHasCompressionMask if compressed.
    # [4] Start of compressed data segment from position zero.
    "data_start",
                        #   If the file has compressed segments, this can be less than
                        #   res_start + res_length.
    # [4] Start of compressed resource segment from position zero.
    "res_start",
    "data_length",      # [4] Length of decompressed data segment.
    "res_length",       # [4] Length of decompressed resource segment.
    "check",            # [1] Does not appear to be used.
    "nonce",            # [4] Does not appear to be used.
    "key_nonce",        # [4] Does not appear to be used.
))

adv_header_t._description = struct.Struct("<BBIIIIBII")
adv_header_t._frombytes = lambda bstr: adv_header_t._make(
    adv_header_t._description.unpack(bstr))

adv_script_t = namedtuple("adv_script_t", ("res_seg", "data_seg"))

def utf8_calc(c: int):
    if c >= 0b11110000:
        return 4
    elif c >= 0b11100000:
        return 3
    elif c >= 0b11000000:
        return 2
    else:
        return 1

class AdvData:
    def __init__(self, header, scpt):
        super().__init__()
        self.header = header
        self.scpt = scpt

class AdvParser:
    def __init__(self, bytesData: bytes):
        self.bytesData = bytesData
        self.parsedData = None
        pass

    def decompress_internal(self, scptbuf: bytes, where: int, full_size: int) -> str:
        """
        Script compression uses a simple backreferencing algorithm.
        A 0x80 byte that is not part of a UTF-8 code unit signals the start of
        a reference. You should then copy `*(tag + 2) + 1` bytes starting from
        `c_pos + ~(*(tag + 1))`.
        """
        nwrit = 0
        out = bytearray(full_size)

        while nwrit < full_size:
            if scptbuf[where] == kADVCTagSignal:
                backstep = ~scptbuf[where + 1]
                cbase = nwrit + backstep
                ncopy = scptbuf[where + 2] + 1

                if ncopy > -backstep:
                    unit_size = -backstep
                    for i in range(ncopy // -backstep):
                        out[nwrit:nwrit + unit_size] = out[cbase:cbase + unit_size]
                        nwrit += unit_size
                else:
                    out[nwrit:nwrit + ncopy] = out[cbase:cbase + ncopy]
                    nwrit += ncopy

                where += kADVCTagLength
            else:
                ncopy = utf8_calc(scptbuf[where])
                out[nwrit:nwrit + ncopy] = scptbuf[where:where + ncopy]
                where += ncopy
                nwrit += ncopy

        return out.decode("utf8")

    def load_script(self, scptbuf: bytes = None) -> adv_script_t:
        if (scptbuf is None):
            scptbuf = self.bytesData
        header = adv_header_t._frombytes(scptbuf[:kADVHeaderLength])
        if header.magic != kADVMagic:
            raise ValueError("Incorrect start byte, it should be kADVMagic.")

        res = None

        if header.data_flags & kADVHasCompressionMask:
            if header.data_flags & kADVHasResSegMask:
                res = self.decompress_internal(scptbuf, header.res_start, header.res_length)
            dat = self.decompress_internal(scptbuf, header.data_start, header.data_length)
        else:
            if header.data_flags & kADVHasResSegMask:
                res = scptbuf[header.res_start:header.res_start + header.res_length].decode("utf8")
            dat = scptbuf[header.res_start:header.data_start + header.data_length].decode("utf8")

        return adv_script_t(res, dat)

    # Use this for object
    def parse(self):
        if self.parsedData is None:
            head = adv_header_t._frombytes(self.bytesData[:kADVHeaderLength])
            scpt = self.load_script(self.bytesData)
            self.parsedData = AdvData(head, scpt)
        return self.parsedData

    def parseJson(self):
        parsedData = self.parse()
        out = {
            "header": parsedData.header,
            "body": {
                "resources": None,
                "data": None
            }
        }

        # flags
        if parsedData.header.data_flags & kADVHasResSegMask:
            out['body']['resources'] = parsedData.scpt.res_seg.split("\n")
        
        data = []
        wasTalkBefore = False
        for line in parsedData.scpt.data_seg.split("\n"):
            if line == "":
                continue
            lineData = line.split(" ")

            if wasTalkBefore: # Text is handled in a very weird way so...
                data.append({
                    "command": "text",
                    "name": lineData[0],
                    "text": lineData[1],
                    "count": lineData[2] if lineData.__len__() >= 3 else None,
                    "additional_param": lineData[3:] if lineData.__len__() >= 4 else None
                })
                wasTalkBefore = False
                continue

            temp = {
                "command": None,
            }

            if lineData[0].startswith("@"):
                temp['command'] = "define" # Variable define
                temp['var_name'] = lineData[0]
                temp['params'] = lineData[1:]
            elif lineData[0] == "&const": # Load const or consts source
                temp['command'] = "const_load"
                temp['var_name' if lineData[1].startswith("@") else "source"] = lineData[1]
            elif lineData[0] == "#main": # Main code
                temp['command'] = "main"
            elif lineData[0] == "waitload": # Wait load
                temp['command'] = "waitload"
            elif lineData[0] == "waitclick": # Wait click
                temp['command'] = "waitclick"
            elif lineData[0] == "click": # Click enable-disable
                temp['command'] = "click"
                temp['value'] = lineData[1]
            elif lineData[0] == "preload": # Preload start command
                temp['command'] = "preload"
                temp['type'] = lineData[1]
                temp['params'] = lineData[2:]
            elif lineData[0] == "fade": # Fade in-out
                temp['command'] = "fade"
                temp['mode'] = lineData[1]
                temp['params'] = lineData[2:]
            elif lineData[0] == "bg": # BG handling
                temp['command'] = "bg"
                temp['mode'] = lineData[2]
                temp['index'] = lineData[1]
                temp['params'] = lineData[3:]
            elif lineData[0] == "cg": # CG handling
                temp['command'] = "cg"
                temp['mode'] = lineData[2]
                temp['index'] = lineData[1]
                temp['params'] = lineData[3:]
            elif lineData[0] == "se": # SE handling
                temp['command'] = "se"
                temp['index'] = lineData[1]
                temp['params'] = lineData[2:]
            elif lineData[0] == "bgmfade": # BGM Fade
                temp['command'] = "bgmfade"
                temp['mode'] = lineData[1]
                temp['value'] = lineData[2]
            elif lineData[0] == "sound": # Sound load
                temp['command'] = "sound"
                temp['mode'] = lineData[1]
                temp['value'] = lineData[2]
            elif lineData[0] == "soundstop": # Sound stop
                temp['command'] = "soundstop"
                temp['mode'] = lineData[1]
                temp['value'] = lineData[2]
            elif lineData[0] == "fadesetting": # Fade Setting
                temp['command'] = "fadesetting"
                temp['mode'] = lineData[1]
                temp['value'] = lineData[2]
            elif lineData[0] == "wait": # Wait
                temp['command'] = "wait"
                temp['value'] = lineData[1]
            elif lineData[0] == "delay": # Delay
                temp['command'] = "delay"
                temp['value'] = lineData[1]
            elif lineData[0] == "enddelay": # End Delay
                temp['command'] = "enddelay"
            elif lineData[0] == "viewing": # Viewing enable/disable
                temp['command'] = "viewing"
                temp['value'] = lineData[1]
                temp['params'] = lineData[2] if lineData.__len__() > 2 else None
            elif lineData[0] == "effection": # Effection?
                temp['command'] = "effection"
                temp['value'] = lineData[1]
                temp['params'] = lineData[2] if lineData.__len__() > 2 else None
            elif lineData[0] == "label": # Label load
                temp['command'] = "label"
                temp['mode'] = lineData[1]
                temp['value'] = lineData[2] if lineData.__len__() > 2 else None
                wasTalkBefore = True
            elif lineData[0] == "window": # Window handling
                temp['command'] = "window"
                temp['mode'] = lineData[1]
                temp['value'] = lineData[2]
            elif lineData[0] == "ch": # Character handler
                temp['command'] = "character"
                temp['mode'] = lineData[2]
                temp['id'] = lineData[1]
                temp['params'] = lineData[3:]
                if (lineData[2] == "talk"):
                    wasTalkBefore = True
            else:
                print("Missing %s" % line)
                temp['command'] = "unknown"
                temp['original'] = line

            data.append(temp)
        
        # Put data list into object
        out['body']['data'] = data

        return json.dumps(out)

if __name__ == '__main__':
    with open(sys.argv[1], "rb") as scpt:
        scptbuf = scpt.read()
        advParser = AdvParser(scptbuf)
        print(advParser.parseJson())