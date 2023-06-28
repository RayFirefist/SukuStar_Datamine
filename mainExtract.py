from lib.sifas_db import AssetDumper
from lib.sifas_api import JapaneseSifasApi as SifasApi

api = SifasApi()
api.login()
assets = AssetDumper(api)

# assets = AssetDumper(None)
# assets.test()
# assets.extractLive2dSdModel()
assets.extractTexture()