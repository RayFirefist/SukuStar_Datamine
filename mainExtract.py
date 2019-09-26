from lib.sifas_db import AssetDumper
from lib.sifas_api import SifasApi

api = SifasApi()
api.loginStartUp()
assets = AssetDumper(api)

# assets = AssetDumper(None)
# assets.test()
assets.extractBackground()