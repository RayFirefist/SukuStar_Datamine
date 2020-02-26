import requests
import random
import urllib.parse

class FireBase:
    #version: 1.1.0
    def __init__(self, platform, version):
        self.SENDER_ID = "581776171271"
        self.version = version

        self.android_id = None
        self.security_token = None
        self.session = requests.session()

        if platform == "android":
            self.GOOGLE_APP_ID = "1:581776171271:android:fc1a9b49d6829936"
            self.platform = 1
        elif platform == "ios":
            self.GOOGLE_APP_ID = "1:581776171271:ios:fc1a9b49d6829936"
            self.platform = 2
        else:
            raise Exception("Platform unknown")

        MODEL_POOL = [
            "iPhone7,2","iPhone7,1","iPhone8,1","iPhone8,2","iPhone8,4","iPhone9,1","iPhone9,3","iPhone9,2",
            "iPhone9,4","iPhone10,1","iPhone10,4","iPhone10,2","iPhone10,5","iPhone10,3","iPhone10,6",
            "iPhone11,8","iPhone11,2","iPhone11,6"
        ]
        self.model = random.choice(MODEL_POOL)

    def sendProvisioning(self, logging_id):
        url = "https://device-provisioning.googleapis.com/checkin"
        header = {
            "Content-Type": "application/json",
            "User-Agent": "allstars/5 CFNetwork/889.9 Darwin/17.2.0",
            "Accept-Language": "ja-jp",
        }
        payload = {
            "locale": "ja_JP",
            "digest": "",
            "checkin": {
                "iosbuild": {
                    "model": self.model,
                    "os_version": "IOS_13.1.3"
                },
                "last_checkin_msec": 0,
                "user_number": 0,
                "type": 2
            },
            "time_zone": "Asia/Tokyo",
            "user_serial_number": 0,
            "id": 0,
            "logging_id": logging_id,
            "version": 2,
            "security_token": 0,
            "fragment": 0
        }
        r = self.session.post(url, json=payload, headers=header)
        return r.json()

    def send(self, android_id, security_token, version_info):
        url = "https://fcmtoken.googleapis.com/register"
        header = {
            "X-firebase-client": "apple-sdk/16B91 fire-analytics/6.0.1 fire-cpp-arch/arm64 fire-cpp-os/ios fire-cpp-stl/libcpp fire-cpp/6.1.0 fire-fcm/4.0.2 fire-iid/4.2.3 fire-ios/6.0.1 fire-unity-ver/2018.4.2f1 fire-unity/6.1.1 xcode/10B61",
            "Authorization": "AidLogin {}:{}".format(android_id, security_token),
            "Accept-Encoding": "br, gzip, deflate",
            "Accept-Language": "ja-jp",
            "app": "com.klab.lovelive.allstars",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "allstars/5 CFNetwork/889.9 Darwin/17.2.0",
            "info": version_info
        }
        payload = {
            "X-osv":"13.1.3",
            "device": android_id,
            "X-scope":"*",
            "plat":"2",
            "app":"com.klab.lovelive.allstars",
            "app_ver": self.version,
            "X-cliv":"fiid-4.0.2",
            "sender": self.SENDER_ID,
            "X-subtype": self.SENDER_ID,
            "appid": "flwR3HuElh4", #TODO:idk
            "gmp_app_id": self.GOOGLE_APP_ID
        }
        r = self.session.post(url, payload, headers=header)
        return r.text

    def getToken(self):
        r = self.sendProvisioning(random.randint(0, 0xFFFFFFFF))
        #print(r)
        self.android_id = str(r['android_id'])
        self.security_token = str(r['security_token'])
        version_info = r['version_info']
        r = self.send(self.android_id, self.security_token, version_info)
        r = urllib.parse.parse_qs(r)
        return r['token'][0]