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


class SIFAS:
    def __init__(self):
        self.uid = 0
        self.sequence = 1
        self.authCount = 1
        self.manifestVersion = "0"
        self.s = requests.session()
        self.sessionKey = b"i0qzc6XbhFfAxjN2"

    def sign(self, endpoint, data):
        endpoint = endpoint.encode("utf8")
        data_ = data.encode("utf8")
        print(b"/" + endpoint + b" " + data_)
        signature = hmac.new(self.sessionKey, b"/" + endpoint + b" " + data_, sha1).hexdigest()
        result = '[%s,"%s"]' % (data, signature)
        return result

    def xor(self, a, b):
        result = bytearray()
        for i in range(len(a)):
            result.append(a[i] ^ b[i])
        return result

    def send(self, endpoint, data):
        url = "https://jp-real-prod-v4tadlicuqeeumke.api.game25.klabgames.net/ep1002/" + endpoint
        params = {"p": "a", "id": self.sequence, "t": int(time.time()*1000)}  # p=platform, id=request sequence
        self.sequence += 1
        headers = {
            "user-agent": "okhttp/3.9.1",
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
        r = self.s.post(url, params=params, data=data, headers=headers, verify=False)
        rr = r.json()
        return rr[3]

    def startup(self):
        rnd = os.urandom(0x20)
        pub = serialization.load_pem_public_key(
            open("klb.pub", "rb").read(),
            backend=default_backend()
        )

        r = self.send("login/startup", {
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
        auth_key = base64.b64decode(r['authorization_key'])
        self.sessionKey = self.xor(auth_key, rnd)
        self.manifestVersion = "7098477e95883aca"

    def login(self):
        rnd = os.urandom(0x20)
        pub = serialization.load_pem_public_key(
            open("klb.pub", "rb").read(),
            backend=default_backend()
        )

        r = self.send("login/login", {
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


