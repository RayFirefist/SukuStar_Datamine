import hmac
from hashlib import sha1
from urllib import parse
import base64
import json
import os
import requests
import time
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

from lib.sifas_api.endpoints import SifasEndpoints


class SifasApi:
    def __init__(self, credentials="./config/credentials.json"):
        self.credentialsFile = credentials
        # setup useful variables
        self.uid = 0
        self.sequence = 1
        self.authCount = 1
        self.manifestVersion = "0"
        self.s = requests.session()
        self.sessionKey = b"i0qzc6XbhFfAxjN2"
        self.authorizationKey = ""
        self.rnd=None
        self.url = "https://jp-real-prod-v4tadlicuqeeumke.api.game25.klabgames.net/ep1002/"
        # account
        try:
            jsonCred = json.loads(open(credentials, "r").read())
            try:
                self.uid = jsonCred['user_id']
            except KeyError:
                print("Failed to parse user id")
            try:
                self.authorizationKey = jsonCred['authorization_key']
                self.pw = jsonCred['password']
                self.sessionKey = self.xor(self.sessionKey, base64.b64decode(self.pw))
            except KeyError:
                print("Failed to create session key")
            try:
                self.authCount = jsonCred['authorization_count']
            except KeyError:
                print("Failed to obtain authorization counter")
        except:
            print("Failed to parse credentials file")

    def sign(self, endpoint, data):
        endpoint = endpoint.encode("utf8")
        data_ = data.encode("utf8")
        print(endpoint + b" " + data_)
        signature = hmac.new(self.sessionKey, endpoint + b" " + data_, sha1).hexdigest()
        result = '[%s,"%s"]' % (data, signature)
        return result

    def updateFile(self):
        open(self.credentialsFile, "w").write(
            json.dumps(
                {
                    "user_id": self.uid,
                    "authorization_key": self.authorizationKey,
                    "authorization_count": self.authCount,
                    "password": base64.b64encode(self.pw).decode("utf-8"),
                    "rnd": base64.b64encode(self.rnd).decode("utf-8")
                }
            )
        )

    def xor(self, a, b):
        result = bytearray()
        for i in range(len(a)):
            result.append(a[i] ^ b[i])
        return result

    def send(self, endpoint : SifasEndpoints, data : dict):
        endpoint = endpoint.value
        url = self.url + endpoint
        params = {"p": "i", "id": self.sequence, "t": int(time.time()*1000)}
        self.sequence += 1
        headers = {
            "user-agent": "allstars/1 CFNetwork/978.0.7 Darwin/18.7.0",
            "content-type": "application/json"
        }

        if params['id'] == 1:
            del(params["t"])

        if self.manifestVersion != "0":
            params["mv"] = self.manifestVersion
        if self.uid > 0:
            params['u'] = str(self.uid)

        if data is not None:
            data = json.dumps(data, separators=(',', ':')).replace("=", "\u003d")
        else:
            data = "null"

        url_ = endpoint + "?" + parse.urlencode(params)
        data = self.sign(url_, data)
        print(data)
        response = self.s.post(url, params=params, data=data, headers=headers)
        
        if response.status_code == 200:
            rr = response.text
            print(rr)
            jsonData = json.loads(rr)
            self.manifestVersion = jsonData[1]
            return jsonData[3]
        else:
            try:
                response.headers['X-Maintenance']
                raise Exception("Maintenance")
            except KeyError:
                pass
            raise Exception("HTTP not 200 (%i)" % response.status_code)

    def loginStartUp(self):
        rnd = os.urandom(0x20)
        pub = serialization.load_pem_public_key(
            open("./lib/sifas_api/klb.pub", "rb").read(),
            backend=default_backend()
        )

        r = self.send(SifasEndpoints.LOGIN_STARTUP, {
            "mask": str(base64.b64encode(pub.encrypt(
                rnd,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA1()),
                    algorithm=hashes.SHA1(),
                    label=None
                )
            )), encoding="utf8"),
            "resemara_detection_identifier": "",
            "time_difference": 32400
        })
        print(r)
        self.uid = r['user_id']
        self.authorizationKey = r['authorization_key']
        auth_key = base64.b64decode(self.authorizationKey)
        self.sessionKey = self.xor(auth_key, rnd)
        self.pw = self.xor(auth_key, self.sessionKey)
        self.rnd = rnd
        self.manifestVersion = "7098477e95883aca"
        self.login()

    def login(self):
        rnd = os.urandom(0x20)
        pub = serialization.load_pem_public_key(
            open("./lib/sifas_api/klb.pub", "rb").read(),
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
            "asset_state": "Fh4FtvLJex9EY7YMhTa2Nze+0+w1r6/Y7gVO8i6ZXpph8rYrHtS9DbQQaNerMIWoGoLsUzlVMnUD62/xUhCNoWw9ahMyXqenHg=="
        })
        self.authCount += 1
        self.updateFile()

    # This allows to give you back a list of URLs which you can use for download packs from remote server
    def assetGetPackUrl(self, packs:list):
        r = self.send(SifasEndpoints.ASSET_GETPACKURL, {"pack_names": packs})
        return r['url_list']

