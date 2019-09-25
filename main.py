from lib.sifas_api import SifasApi
from lib.sifas_api.endpoints import SifasEndpoints

api = SifasApi()

print(SifasEndpoints.ASSET_GETPACKURL.value)
api.makeRequest(SifasEndpoints.ASSET_GETPACKURL.value)