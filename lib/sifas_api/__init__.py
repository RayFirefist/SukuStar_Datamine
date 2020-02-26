import json
import os
import base64

from lib.sifas_api.sifas import SIFAS

class JapaneseSifasApi(SIFAS):
    def __init__(self, credentialsPath: str = "./config/credentials_ja.json", pf: int = 1, skip_fb: bool = False):
        super().__init__(pf=pf, version="JP", skip_fb=skip_fb)
        self.configPath = credentialsPath
        self.lang = "ja"
        if os.path.exists(credentialsPath):
            try:
                data = json.loads(open(credentialsPath, 'r').read())
                try:
                    self.uid = data['user_id']
                except KeyError:
                    pass
                try:
                    self.authCount = data['authorization_count']
                except KeyError:
                    pass
                try:
                    self.pw = base64.b64decode(data['password'])
                except KeyError:
                    pass
            except json.decoder.JSONDecodeError as e:
                print("JSON Failed to be decoded due to: %s" % e.msg)
        pass

class WorldwideSifasApi(SIFAS):
    def __init__(self, credentialsPath: str = "./config/credentials_ww.json", pf: int = 1, skip_fb: bool = False, language: str = 'en'):
        super().__init__(pf=pf, version="WW", skip_fb=skip_fb)
        self.configPath = credentialsPath
        self.lang = language
        if os.path.exists(credentialsPath):
            data = json.loads(open(credentialsPath, 'r').read())
            try:
                self.uid = data['user_id']
            except KeyError:
                pass
            try:
                self.authCount = data['authorization_count']
            except KeyError:
                pass
            try:
                self.pw = base64.b64decode(data['password'])
            except KeyError:
                pass
        pass