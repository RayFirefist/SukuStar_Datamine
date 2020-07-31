
# Tweaked version of sifas.py made by https://github.com/kotori2

import hmac
from hashlib import sha1, md5
from urllib import parse
import base64
import json
import os
import requests
import time
import random
import sqlite3
import binascii
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
import urllib3, copy
from lib.sifas_api.jackpot import JackpotCore
from lib.sifas_api.firebase import FireBase
from lib.sifas_api.constants import *
import re

urllib3.disable_warnings()

import collections

import zlib

# Ray's libs
from lib.sifas_api.endpoints import SifasEndpoints
from lib.penguin import masterDataRead, decrypt_stream, FileStream

def dict_merge(dct, merge_dct):
    for k, v in merge_dct.items():
        if k in dct and isinstance(dct[k], dict) and isinstance(merge_dct[k], collections.Mapping):
            dict_merge(dct[k], merge_dct[k])
        elif k in dct and isinstance(dct[k], list) and isinstance(merge_dct[k], list):
            if len(merge_dct[k]):
                keys = merge_dct[k][::2]
                dic = copy.deepcopy(merge_dct[k])
                for k, v in zip(dct[k][::2], dct[k][1::2]):
                    if k not in keys:
                        dic.append(k)
                        dic.append(v)
                dct[k] = dic
        else:
            dct[k] = merge_dct[k]


def dict_merge_repl(dct, merge_dct):
    for k, v in merge_dct.items():
        if k in dct and isinstance(dct[k], dict) and isinstance(merge_dct[k], collections.Mapping):
            dict_merge_repl(dct[k], merge_dct[k])
        elif k in dct and isinstance(dct[k], list) and isinstance(v, list):
            if len(merge_dct[k]):
                dct[k] = merge_dct[k]
        else:
            dct[k] = merge_dct[k]

class SIFAS:
    @staticmethod
    def _constructDict(src, index=None):
        result = []
        cnt = 1
        for i in src:
            if index is None:
                result.append(cnt)
            else:
                result.append(i[index])
            result.append(i)
            cnt += 1
        return result

    @staticmethod
    def _parseArray(src):
        cnt = 0
        result = []
        for i in src:
            cnt += 1
            if cnt % 2 == 1:
                continue
            result.append(i)

        return result

    @staticmethod
    def _parseDict(src):
        result = {}
        for x, y in zip(src[::2], src[1::2]):
            result[x] = y
        return result

    @staticmethod
    def _parseDictKeys(src):
        return src[::2]

    def __init__(self, pf, version="JP", skip_fb=False):
        if version == "WW":
            self.version = "WW"
            self.server = "ww"
            consts = VERSION_CONSTANTS_WW
        else:
            self.version = "JP"
            self.server = "ja"
            consts = VERSION_CONSTANTS_JP

        self.debug = False
        self.lang = "en"
        self.consts = consts
        self.ep = consts['ep']
        self.baseKeys = consts['keys']
        self.uid = 0
        self.sequence = 1
        self.authCount = 1
        self.versionCode = consts["versionName"]
        self.sessionKey = consts['sessionKey']
        if self.version == "JP":
            self.DMcryptoKey = bytes.fromhex("2f4011d553fca4cf9e970e4c5f3d959500e286b53be46ec9ce687b2c31ec5767")
            self.ServerEventReceiverKey = bytes.fromhex("31f1f9dc7ac4392d1de26acf99d970e425b63335b461e720c73d6914020d6014") # ServerEventReceiverKey
        else:
            self.DMcryptoKey = bytes.fromhex("78d53d9e645a0305602174e06b98d81f638eaf4a84db19c756866fddac360c96")
            self.ServerEventReceiverKey = bytes.fromhex("31f1f9dc7ac4392d1de26acf99d970e425b63335b461e720c73d6914020d6014") # ServerEventReceiverKey
        self.manifestVersion = "0"
        if os.path.exists("manifest_%s" % self.version.lower()):
            self.manifestVersion = open("manifest_%s" % self.version.lower(), "r", encoding="utf8").read()
        else:
            self.manifestVersion = "afc51b21514855fd"
        self.device = self.genDeviceModel(pf)
        if pf == 2:
            self.platform = "android"
            self.jackpot = JackpotCore("arm64", consts)
        else:
            self.platform = "ios"
            self.jackpot = JackpotCore("macho64", consts)

        fb = FireBase(self.platform, self.versionCode)
        if not skip_fb:
            print("Generating firebase token...")
            self.devToken = fb.getToken()
            print("Generated")
        else:
            self.devToken = ""

        self.s = requests.session()
        self.retryCount = 0
        self.pw = None
        self.userModel = collections.defaultdict(list)

        self.conn = sqlite3.connect("masterdata.db")
        self.conn.row_factory = sqlite3.Row
        self.cur = self.conn.cursor()

    @staticmethod
    def genDeviceModel(pf):
        if pf == 1:
            model_tbl = [
                "iPhone6", "iPhone6Plus", "iPadMini3Gen", "iPadAir2", "iPhone6S", "iPhone6SPlus",
                "iPadPro1Gen", "iPadMini4Gen", "iPhoneSE1Gen", "iPadPro10Inch1Gen", "iPhone7",
                "iPhone7Plus", "iPodTouch6Gen", "iPad5Gen", "iPadPro2Gen", "iPadPro10Inch2Gen",
                "iPhone8", "iPhone8Plus", "iPhoneX", "iPhoneXS", "iPhoneXSMax", "iPhoneXR",
                "iPadPro11Inch", "iPadPro3Gen"
            ]
        else:
            model_tbl = [
                "OnePlus GM1913", "OnePlus GM1903", "OnePlus ONEPLUS A6000", "OnePlus ONEPLUS A5000",
                "OnePlus ONEPLUS A3010", "OnePlus ONEPLUS A3000", "Xiaomi Redmi Note 7 Pro",
                "Xiaomi MI 9", "Xiaomi Redmi K20 Pro", "Xiaomi Redmi Note 7", "Xiaomi MI 8",
                "Xiaomi MIX 2S", "Xiaomi Redmi 4X", "Xiaomi MI 6", "Xiaomi MI 9 SE", "Xiaomi MIX 2",
                "Xiaomi Mix", "vivo vivo X20", "Xiaomi Redmi Note 4X", "samsung SM-N9760",
                "samsung SM-G977B", "samsung SM-G9650", "samsung SM-W2018", "samsung SM-N9600",
                "samsung SM-G9650", "samsung SM-N9500", "samsung SM-G9550", "samsung SM-G9350",
                "samsung SM-N9200", "samsung SM-G9006V", "samsung GT-I9500", "OPPO OPPO R11s",
                "OPPO Find7", "OPPO PBET00", "OPPO PAFM00", "vivo vivo NEX", "Google Pixel 3 XL",
                "Google Pixel 2 XL", "Google Pixel XL", "motorola Nexus 6", "Sony H8324", "Sony H8342",
                "Sony G8342", "Sony G8342", "Sony G8341", "Sony G8142", "Sony G8141", "Sony D6603",
                "Sony D6603", "HUAWEI EVA-AL10"
            ]
        return random.choice(model_tbl)

    def dump(self):
        '''kw = [self.uid, self.authCount,
              binascii.hexlify(self.sessionKey).decode("u8"),
              binascii.hexlify(self.pw).decode("u8"),
              self.manifestVersion,
              ]'''
        kw = {
            "user_id": self.uid,
            "password": base64.b64encode(self.pw).decode('utf-8'),
            "autorization_count": self.authCount
        }
        try:
            open(self.configPath, "w+").write(json.dumps(kw))
        except:
            open("sifas.json", "w+").write(json.dumps(kw))

    def load(self):
        self.uid, self.authCount, sessionKey, pw, self.manifestVersion = json.loads(open("sifas.json").read())
        self.sessionKey = binascii.unhexlify(sessionKey.encode("u8"))
        self.pw = binascii.unhexlify(pw.encode("u8"))

    def sign(self, endpoint, data, macOverride=None):
        if macOverride is None:
            endpoint = endpoint.encode("utf8")
            data_ = data.encode("utf8")
        # print("sign with", self.sessionKey)
            signature = hmac.new(self.sessionKey, b"/" + endpoint + b" " + data_, sha1).hexdigest()
        else:
            signature = macOverride
        result = '[%s,"%s"]' % (data, signature)
        return result

    def xor(self, a, b):
        result = bytearray()
        for i in range(len(a)):
            result.append(a[i] ^ b[i])
        return bytes(result)

    def getEP(self):
        return "%s/" % self.consts["fullEp"]

    def send(self, endpoint, data, hash=None, params_override={}):
        if type(endpoint) == SifasEndpoints:
            endpoint = endpoint.value
        if endpoint[0] == "/":
            endpoint = endpoint[1:]
        if hash:
            print("Override: " + hash)
        print(endpoint)
        params = {"p": "a", "mv": None, "id": self.sequence, "u": None, "l": None,
                  "t": int(time.time() * 1000)}  # p=platform, id=request sequence
        url = self.getEP() + endpoint
        if self.version == "WW":
            params['l'] = self.lang
        else:
            del(params['l'])
        if self.platform == "android":
            headers = {
                "user-agent": "okhttp/3.9.1",
                "content-type": "application/json"
            }
        else:
            params["p"] = "i"
            headers = {
                "User-Agent": "allstars/1 CFNetwork/1121.2.2 Darwin/19.2.0",
                "Accept-Language": "ja-jp",
                "Content-Type": "application/json"
            }

        self.sequence += 1

        # if params['id'] == 1 and self.platform == 2:
        #     del(params["t"])

        if self.manifestVersion != "0":
            params["mv"] = self.manifestVersion
        else:
            del (params["mv"])
        if self.uid > 0:
            params['u'] = str(self.uid)
        else:
            del (params["u"])

        data_ = data

        if data is not None:
            data = json.dumps(data, separators=(',', ':')).replace("=", "\u003d")
        else:
            data = "null"

        if params_override:
            params = params_override

        url_ = endpoint + "?" + parse.urlencode(params)
        data = self.sign(url_, data, hash)
        #print(data)
        # print(url_, data, params, headers)
        r = self.s.post(url, params=params, data=data, headers=headers,
                        # verify=False, proxies={"https": "127.0.0.1:8888"}
                        )

        if self.debug: 
            print(url)
            print(r.text)
        # print(r.text)
        if r.status_code != 200:
            print("Error http {} on {}".format(r.status_code, endpoint))
            print(r.text)
            if r.status_code == 410:
                print("CLIENT UPGRADE REQUIRED!!!")
                time.sleep(0xFFFFFFFF)
            elif r.status_code == 504 and self.retryCount < 5:
                print("Retry: {}".format(self.retryCount))
                self.retryCount += 1
                r = self.send(endpoint, data)
                print(r)
                return r
            elif r.status_code == 503:
                print("503: Service unavailable (maintenance?) due to:\n%s" % r.json()['message_%s' % self.lang])
                raise Exception("Service unavailable")
            else:
                print("Not retry: {}".format(self.retryCount))
                print(r.text)
                raise Exception("HTTP Error {}".format(r.status_code))
        else:
            self.retryCount = 0
            ts, manifestVersion, code, data, hashx = r.json()
            if "user_model" in data:
                # print("\n\n\nuser_model update >", data["user_model"])
                dict_merge_repl(self.userModel, data["user_model"])

            if "user_model_diff" in data:
                # print("\n\n\nuser_model_diff update >", data["user_model_diff"])
                dict_merge(self.userModel, data["user_model_diff"])

            if self.manifestVersion != manifestVersion:
                print("New manifest version: " + manifestVersion)
                self.manifestVersion = manifestVersion
                open("manifest_%s" % self.version.lower(), "w", encoding="utf8").write(self.manifestVersion)

            return data

    def retreive(self, endpoint):
        ep = self.getEP()
        url = ep + endpoint
        response = requests.get(url)
        if response.status_code == 200:
            return response.content
        else:
            raise Exception("GET failed due to HTTP (%i) on %s" %
                            (response.status_code, url))

    def startup(self):
        self.sequence = 1
        self.authCount = 1
        rnd = os.urandom(0x20)
        pub = serialization.load_pem_public_key(
            self.consts["cert"],
            backend=default_backend()
        )

        device_id = os.urandom(0x20).hex()
        if self.platform == 1:
            device_id = device_id.upper()

        r = self.send(SifasEndpoints.LOGIN_STARTUP, {
            "mask": str(base64.b64encode(pub.encrypt(
                rnd,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA1()),
                    algorithm=hashes.SHA1(),
                    label=None
                )
            )), encoding="utf8"),
            "resemara_detection_identifier": device_id,
            "time_difference": 0
        })
        self.uid = r['user_id']
        auth_key = base64.b64decode(r['authorization_key'])
        self.sessionKey = self.xor(auth_key, rnd)
        # self.sessionKey = self.xor(self.DMcryptoKey, self.sessionKey)
        self.pw = self.sessionKey

    def login(self):
        self.sequence = 1
        if self.pw is not None:
            self.sessionKey = self.pw
        rnd = os.urandom(0x20)
        pub = serialization.load_pem_public_key(
            self.consts["cert"],
            backend=default_backend()
        )

        r = self.send(SifasEndpoints.LOGIN_LOGIN, {
            "mask": str(base64.b64encode(pub.encrypt(
                rnd,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA1()),
                    algorithm=hashes.SHA1(),
                    label=None
                )
            )), encoding="utf8"),
            "user_id": self.uid,
            "auth_count": self.authCount,
            "asset_state": self.jackpot.AssetStateLogGenerateV2(
                base64.b64encode(rnd)
            )
        })

        if 'authorization_count' in r:
            self.authCount = r['authorization_count'] + 1
            print("Fixed auth count: {}".format(self.authCount))
            self.login()
            return

        session_key = base64.b64decode(r['session_key'])
        self.sessionKey = self.xor(session_key, rnd)
        self.sessionKey = self.xor(self.ServerEventReceiverKey, self.sessionKey)
        ja_key = '78d53d9e645a0305602174e06b98d81f638eaf4a84db19c756866fddac360c96'
        self.sessionKey = self.xor(bytes.fromhex(ja_key), self.sessionKey)
        self.authCount += 1
        self.dump()

    def assetGetPackUrl(self, pkgs: list):
        r = self.send(SifasEndpoints.ASSET_GETPACKURL, {"pack_names": pkgs})
        return r['url_list']

    def termsAgreement(self):
        r = self.send(SifasEndpoints.TERMS_AGREEMENT, {"terms_version": 1})
        pass

    # This allows to get the list of database
    def getDbList(self):
        return masterDataRead(
            FileStream(
                self.retreive(
                    "static/%s/masterdata_%s_%s" % (self.manifestVersion, "i" if self.platform == "ios" else "a", self.lang)
                )
            )
        )

     # Downloads the databases and saves them into /assets/db
    def downloadDbs(self, dbsList: dict = None, assetsPath="./assets/"):
        server = "ja" if self.version.lower() == "jp" else "ww"
        try:
            os.makedirs(assetsPath + "db/")
        except FileExistsError:
            pass
        if dbsList is None:
            dbsList = self.getDbList()
        for database in dbsList:
            print("Obtaining %s" % database['db_name'])
            baseFile = self.retreive("/static/%s/%s" %
                                     (self.manifestVersion, database['db_name']))
            decrypted = decrypt_stream(
                server, baseFile, database['db_keys_list'][0], database['db_keys_list'][1], database['db_keys_list'][2])
            deflated = zlib.decompress(decrypted, -zlib.MAX_WBITS)
            open("%sdb/%s" %
                 (assetsPath, database['db_name']), "wb").write(deflated)
        print("Version %s" % self.manifestVersion)
        open("%sdb/version" % (assetsPath), "w").write(self.manifestVersion)
