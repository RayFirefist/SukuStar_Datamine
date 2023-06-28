import os

from lib.sifas_api import JapaneseSifasApi, WorldwideSifasApi

try:
    print("Japanese server")
    api = JapaneseSifasApi()
    api.startup()
    api.login()
    print("Japanese server generated")
except Exception as e:
    print(f"failed due to {e}")

try:
    print("Worldwide server")
    api = WorldwideSifasApi()
    api.startup()
    api.login()
    print("Worldwide server generated")
except Exception as e:
    print(f"failed due to {e}")