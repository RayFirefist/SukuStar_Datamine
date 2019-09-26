import requests
import json
import os
import time

import logging

#import curlify

from hyper import HTTPConnection

import base64
import hmac
from hashlib import sha1
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding


logging.basicConfig(level=logging.DEBUG)

class SifasApi:

    def __init__(self, credentialsPath:str="./config/credentials.json"):
        # credentials data
        self.credentialsData = json.loads(open(credentialsPath, "r").read())
        # Server elements
        self.serverUrl = "https://jp-real-prod-v4tadlicuqeeumke.api.game25.klabgames.net"
        self.endpoint = "/ep1002/"
        # Flags
        self.sequence = 1
        try:
            self.authCount = self.credentialsData['auth_count']
        except:
            self.authCount = 1
        # Initial session key
        self.sessionKey = "i0qzc6XbhFfAxjN2".encode("utf8")
        self.manifestVersion = ""
        # part of the requests
        self.params = {
            "p": "a",
            "id": self.sequence,
            "u": self.credentialsData['user_id'],
            "t": int(time.time()*1000)
        }
        self.headers = headers = {
            'Content-Type': "application/json",
            'User-Agent': "allstars/1 CFNetwork/978.0.7 Darwin/18.7.0",
            'Accept': "*/*",
            'Host': "jp-real-prod-v4tadlicuqeeumke.api.game25.klabgames.net",
            'Accept-Encoding': "gzip, deflate",
            'Content-Length': "380",
            'Connection': "keep-alive",
            'cache-control': "no-cache"
        }

    def updateTime(self):
        self.params["t"] = int(time.time()*1000)
        pass

    def updateManifestVersion(self, manifestVersion):
        self.params['mv'] = manifestVersion
        pass

    def updateSequence(self):
        self.params['id'] = self.sequence
        self.sequence += 1
        pass

    def xor(self, a, b):
        result = bytearray()
        for i in range(len(a)):
            result.append(a[i] ^ b[i])
        return result

    # Creates the signature for request
    def sign(self, endpoint:str, data):
        endpoint = endpoint.encode("utf8")
        if type(data) == dict:
            data = json.dumps(data)
        data_ = data.encode("utf8")
        print(b"/" + endpoint + b" " + data_)
        signature = hmac.new(self.sessionKey, b"/" + endpoint + b" " + data_, sha1).hexdigest()
        result = '[%s,"%s"]' % (data, signature)
        return result

    # Principal request function
    def makeRequest(self, endpoint:str, data:dict={}):
        if endpoint[0] == "/":
            endpoint = endpoint[1:]

        connection = HTTPConnection(self.serverUrl)

        self.updateSequence()
        self.updateTime()

        url = self.serverUrl + self.endpoint + endpoint
        params = self.params

        if data is not None:
            data = json.dumps(data, separators=(',', ':')).replace("=", "\u003d")
        else:
            data = "null"

        if not self.manifestVersion == "":
            params['mv'] = self.manifestVersion
        if params['u'] == 0:
            del params['u']

        params_url = "?"
        for x, y in params:
            params_url += "%s=%s&" % x, y

        request = connection.request("POST", self.endpoint + endpoint + params_url, headers=self.headers, body=json.dumps(self.sign(endpoint, data)).encode("utf8"))
        
        #response = requests.post(url, data=, params=self.params, headers=self.headers)

        response = connection.get_response(request)
        data = response.read()

        #sprint(curlify.to_curl(response.request))

        if response.status_code == 200:
            print(response.text)
            return json.loads(response.text)
        else:
            print(response.headers)
            try:
                response.headers['X-Maintenance']
                raise Exception("Maintenance")
            except KeyError:
                pass
            errorMessage = "ERROR HTTP %i : %s" % (response.status_code, response.text)
            print(errorMessage)
            raise Exception("HTTP status not 200 (%i)" % response.status_code)

    def prepareLogin(self):
        rnd = os.urandom(0x20)
        pub = serialization.load_pem_public_key(
            open("./lib/sifas_api/klb.pub", "rb").read(),
            backend=default_backend()
        )
        return rnd, pub

    def loginStartUp(self):
        rnd, pub = self.prepareLogin()
        self.params['u'] = 0

        r = self.makeRequest("login/startup", data={
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
        self.params['u'] = r['user_id']
        auth_key = base64.b64decode(r['authorization_key'])
        self.sessionKey = self.xor(auth_key, rnd)
        self.manifestVersion = "7098477e95883aca"

    def login(self):
        rnd, pub = self.prepareLogin()

        r = self.makeRequest("login/login", data={
            "mask": str(base64.b64encode(pub.encrypt(
                rnd,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA1()),
                    algorithm=hashes.SHA1(),
                    label=None
                )
            )), encoding="utf8"),
            "user_id": self.credentialsData['user_id'],
            "auth_count": self.authCount,
            "asset_state": "Fh4FtvLJex9EY7YMhTa2Nze+0+w1r6/Y7gVO8i6ZXpph8rYrHtS9DbQQaNerMIWoGoLsUzlVMnUD62/xUhCNoWw9ahMyXqenHg=="
        })

        self.authCount += 1
        pass


    pass