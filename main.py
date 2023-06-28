from lib.sifas_api import JapaneseSifasApi
from lib.sifas_api.endpoints import SifasEndpoints

api = JapaneseSifasApi()

api.login()
api.downloadDbs()