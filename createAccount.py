import os

from lib.sifas_api import JapaneseSifasApi, WorldwideSifasApi

print("Japanese server")
api = JapaneseSifasApi()
api.startup()
api.login()
print("Japanese server generated")
print("Worldwide server")
api = WorldwideSifasApi()
api.startup()
api.login()
print("Worldwide server generated")