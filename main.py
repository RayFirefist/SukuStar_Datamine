from lib.sifas_api import SifasApi
from lib.sifas_api.endpoints import SifasEndpoints

api = SifasApi()

api.loginStartUp()
api.downloadDbs()