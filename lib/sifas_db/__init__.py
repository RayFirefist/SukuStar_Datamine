# os lib
import os
# HTTP request
import requests
# DB lib
import sqlite3
# zlib
import zlib
# SIFAS API
from lib.sifas_api import SifasApi
from lib.sifas_api.endpoints import SifasEndpoints
# Decrypt
from lib.penguin import decrypt_stream

class AssetDumper:

    def __init__(self, sifasApi:SifasApi, assetsPath="./assets/", language="ja"):
        self.assetsPath = assetsPath
        self.api = sifasApi
        self.assets = sqlite3.connect(assetsPath + "db/asset_i_%s_0.db" % language)
        print(self.assets)
        self.packs = {}
        try:
            os.makedirs("%spkg/" % self.assetsPath)
        except FileExistsError:
            pass
        pass

    def downloadPacks(self, packs:list):
        self.packs = {}
        urls = self.api.assetGetPackUrl(packs)
        i = 0
        for url in urls:
            data = b''
            if not os.path.exists("%spkg/%s" % (self.assetsPath, packs[i])):
                print("downloading %s" % packs[i])
                data = requests.get(url).content
                open("%spkg/%s" % (self.assetsPath, packs[i]), "wb").write(data)
            else:
                print("reading %s" % packs[i])
                data = open("%spkg/%s" % (self.assetsPath, packs[i]), "rb").read()
            self.packs[packs[i]] = data
            i+=1
        pass

    def test(self):
        c = self.assets.cursor()
        for row in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall():
            print(row)

    def extractBackground(self):
        try:
            os.makedirs("%s/images/background/" % self.assetsPath)
        except FileExistsError:
            pass
        c = self.assets.cursor()
        bundles = []
        for bundle in c.execute("SELECT DISTINCT pack_name FROM background").fetchall():
            bundles.append(bundle[0])
        # Download the data
        self.downloadPacks(
            bundles
        )
        # Extract the data
        i=0
        for bundle in bundles:
            for fileData in c.execute("SELECT head, size, key1, key2 FROM background WHERE pack_name = '%s'" % bundle).fetchall():
                print("%i.png" % i)
                data = self.packs[bundle][fileData[0]:fileData[0]+fileData[1]]
                print("file size %i" % data.__len__())
                data = decrypt_stream(data, 12345, fileData[2], fileData[3])
                open(self.assetsPath + "images/background/%i.png" % i, "wb").write(data)
                try:
                    data = zlib.decompress(data, -zlib.MAX_WBITS)
                    open(self.assetsPath + "images/background/%i_un.png" % i, "wb").write(data)
                except zlib.error:
                    print("cant uncompress")
                    pass
                i+=1