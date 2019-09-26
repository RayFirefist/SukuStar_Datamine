from lib.sifas_api import SifasApi
from lib.sifas_api.endpoints import SifasEndpoints

api = SifasApi()

#print(SifasEndpoints.ASSET_GETPACKURL.value)
#api.makeRequest("noop/noop")
#api.login()
api.loginStartUp()