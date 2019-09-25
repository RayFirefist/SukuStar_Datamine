import requests
import json

class SifasApi:

    def __init__(self, credentialsPath:str="./config/credentials.json"):
        # ?p=a&id=1
        self.serverUrl = "https://jp-real-prod-v4tadlicuqeeumke.api.game25.klabgames.net/"
        self.endpoint = "ep1002/"
        self.credentialsData = json.dumps(open(credentialsPath, "r").read())

    def makeRequest(self, endpoint:str, method:str="POST", data:dict={}):
        # TODO HEADERS
        response = requests.request(method, self.serverUrl + self.endpoint + endpoint, data=data)

        if response.status_code == 200:
            print(response.text)
            return json.loads(response.text)
        else:
            errorMessage = "ERROR HTTP %i : %s" % (response.status_code, response.text)
            print(errorMessage)
            raise Exception("HTTP status not 200 (%i)" % response.status_code)


    def loginStartUp(self):
        data = self.makeRequest("login/startup")
        return data

    pass