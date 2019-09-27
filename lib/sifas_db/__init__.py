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
# Unity
from lib.unity import UnityAssetBundle
# Base64
import base64

class AssetDumper:

    def __init__(self, sifasApi:SifasApi, assetsPath="./assets/", language="ja"):
        self.assetsPath = assetsPath
        self.api = sifasApi
        self.assets = sqlite3.connect(assetsPath + "db/asset_i_%s_0.db" % language)
        self.master = sqlite3.connect(assetsPath + "db/masterdata.db")
        self.packs = {}
        try:
            os.makedirs("%spkg/" % self.assetsPath)
        except FileExistsError:
            pass
        pass

    def downloadPacks(self, packs:list, forceDownload: bool = False):
        i = 0

        antiDupesPacks = []
        for pack in packs:
            if pack in antiDupesPacks:
                continue
            else:
                antiDupesPacks.append(pack)
        packs = antiDupesPacks

        if forceDownload == False:
            packsNew = []
            for pack in packs:
                if os.path.exists("%spkg/%s" % (self.assetsPath, packs[i])):
                    print("reading %s" % packs[i])
                    data = open("%spkg/%s" % (self.assetsPath, packs[i]), "rb").read()
                    self.packs[packs[i]] = data
                    del packs[i]
                    i+=1
                else:
                    packsNew.append(pack)
            packs = packsNew

        i = 0     
        print(packs) 
        if packs.__len__() > 0:
            urls = self.api.assetGetPackUrl(packs)
            for url in urls:
                print("downloading %s" % packs[i])
                data = requests.get(url).content
                open("%spkg/%s" % (self.assetsPath, packs[i]), "wb").write(data)
                self.packs[packs[i]] = data
                i+=1
            pass

        return antiDupesPacks

    def test(self):
        c = self.assets.cursor()
        for row in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall():
            print(row)

    def extractCardsAssets(self, forceDownload=False):
        path = self.assetsPath + "images/cards/"
        try:
            os.makedirs(path)
        except FileExistsError:
            pass
        mc = self.master.cursor()
        ac = self.assets.cursor()
        assets = mc.execute("SELECT card_m_id, appearance_type, image_asset_path, thumbnail_asset_path, still_thumbnail_asset_path, background_asset_path FROM m_card_appearance").fetchall()
        for asset in assets:
            print("elaboration card %i" % asset[0])
            isAwaken = "awaken" if asset[1] == 2 else "normal"
            # card illustration
            file = open("%stex_card_%i_%s.jpg" % (path, asset[0], isAwaken), "wb")
            file.write(self.extractSingleAssetWithKeys(path="", table="texture", asset_path=asset[2], forceDownload=forceDownload, returnValue=True))
            file.close()
            # thumb illustration
            file = open("%stex_thumb_%i_%s.jpg" % (path, asset[0], isAwaken), "wb")
            file.write(self.extractSingleAssetWithKeys(path="", table="texture", asset_path=asset[3], forceDownload=forceDownload, returnValue=True))
            file.close()
            # still thumb illustration
            file = open("%stex_still_thumb_%i_%s.jpg" % (path, asset[0], isAwaken), "wb")
            file.write(self.extractSingleAssetWithKeys(path="", table="texture", asset_path=asset[4], forceDownload=forceDownload, returnValue=True))
            file.close()
            # bg
            file = open("%stex_bg_%i_%s.jpg" % (path, asset[0], isAwaken), "wb")
            file.write(self.extractSingleAssetWithKeys(path="", table="texture", asset_path=asset[5], forceDownload=forceDownload, returnValue=True))
            file.close()

    def extractStillIllus(self, forceDownload=False):
        path = self.assetsPath + "images/still/"
        try:
            os.makedirs(path)
        except FileExistsError:
            pass
        mc = self.master.cursor()
        ac = self.assets.cursor()
        assets = mc.execute("SELECT still_master_id, display_order, still_asset_path FROM m_still_texture").fetchall()
        for asset in assets:
            print("elaboration still %i" % asset[0])
            # card illustration
            file = open("%stex_still_%i_%i.jpg" % (path, asset[0], asset[1]), "wb")
            file.write(self.extractSingleAssetWithKeys(path="", table="texture", asset_path=asset[2], forceDownload=forceDownload, returnValue=True))
            file.close()

    def extractBackground(self):
        self.extractAssetsWithKeys("%s/images/background/" % self.assetsPath, "background")

    def extractLive2dSdModel(self):
        self.extractAssetsWithKeys("%s/images/live2d/sd_models/" % self.assetsPath, "live2d_sd_model")

    def extractTexture(self):
        self.extractAssetsWithKeys("%s/images/texture/" % self.assetsPath, "texture")

    def extractStage(self):
        self.extractAssetsWithKeys("%s/models/stage/" % self.assetsPath, "stage")

    def extractMemberModels(self):
        self.extractAssetsWithKeys("%s/models/member/" % self.assetsPath, "member_model")
    
    def extractMemberSdModels(self):
        self.extractAssetsWithKeys("%s/sd_models/member/" % self.assetsPath, "member_sd_model")
    
    def extractGachaPerformance(self):
        self.extractAssetsWithKeys("%s/bundles/gachaPerformance/" % self.assetsPath, "gacha_performance")

    def extractSingleAssetWithKeys(self, path, table, asset_path, forceDownload=False, returnValue=False):
        if path != "":
            try:
                os.makedirs(path)
            except FileExistsError:
                pass
        c = self.assets.cursor()
        bundles = []
        if asset_path.find("'") > -1:
            if asset_path.find('"') > -1:
                print("1")
                query = "SELECT pack_name FROM %s WHERE asset_path = '%s'" % (table, asset_path)
            else:
                print("1b")
                query = 'SELECT pack_name FROM %s WHERE asset_path = "%s"' % (table, asset_path)
        else:
            if asset_path.find('"') > -1:
                print("2")
                query = "SELECT pack_name FROM %s WHERE asset_path = '%s'" % (table, asset_path)
            else:
                print("2b")
                query = "SELECT pack_name FROM %s WHERE asset_path = \"%s\"" % (table, asset_path)
        print(query)
        for bundle in c.execute(query).fetchall():
            bundles.append(bundle[0])
        if bundles.__len__() == 0:
            return
        # Download the data
        self.downloadPacks(
            bundles,
            forceDownload
        )
        # Extract the data
        i=0
        for bundle in bundles:
            if asset_path.find("'") > -1:
                if asset_path.find('"') > -1:
                    query = "SELECT head, size, key1, key2, asset_path FROM %s WHERE pack_name = '%s' AND asset_path = '%s'" % (table, bundle, asset_path)
                else:
                    query = 'SELECT head, size, key1, key2, asset_path FROM %s WHERE pack_name = "%s" AND asset_path = "%s"' % (table, bundle, asset_path)
            else:
                if asset_path.find('"') > -1:
                    query = "SELECT head, size, key1, key2, asset_path FROM %s WHERE pack_name = '%s' AND asset_path = '%s'" % (table, bundle, asset_path)
                else:
                    query = 'SELECT head, size, key1, key2, asset_path FROM %s WHERE pack_name = "%s" AND asset_path = "%s"' % (table, bundle, asset_path)
            for fileData in c.execute(query).fetchall():
                if fileData[4] != asset_path:
                    continue
                try:
                    self.packs[bundle]
                except KeyError:
                    self.downloadPacks([bundle], True)
                print("%i.png" % i)
                data = self.packs[bundle][fileData[0]:fileData[0]+fileData[1]]
                print("file size %i" % data.__len__())
                data = decrypt_stream(data, 0x3039, fileData[2], fileData[3], True)
                if returnValue:
                    return data
                else:
                    open("%s/%s.bin" % (path, base64.b64encode(fileData[4].encode("utf-8")).decode("utf-8").replace("/", "_BACK_")), "wb").write(data)
                i+=1
    
    def extractAssetsWithKeys(self, path, table, forceDownload=False):
        try:
            os.makedirs(path)
        except FileExistsError:
            pass
        c = self.assets.cursor()
        bundles = []
        for bundle in c.execute("SELECT pack_name FROM %s" % table).fetchall():
            bundles.append(bundle[0])
        # Download the data
        bundles = self.downloadPacks(
            bundles,
            forceDownload
        )
        # Extract the data
        i=0
        for bundle in bundles:
            print("reading %s" % bundle)
            if bundle.find("'"):
                query = 'SELECT head, size, key1, key2, asset_path FROM %s WHERE pack_name = "%s"' % (table, bundle)
            else:
                query = "SELECT head, size, key1, key2, asset_path FROM %s WHERE pack_name = '%s'" % (table, bundle)
            for fileData in c.execute(query).fetchall():
                try:
                    self.packs[bundle]
                except KeyError:
                    self.downloadPacks([bundle], True)
                print("File no. %i" % i)
                data = self.packs[bundle][fileData[0]:fileData[0]+fileData[1]]
                print("file size %i" % data.__len__())
                decData = decrypt_stream(data, 0x3039, fileData[2], fileData[3], True)
                print(decData[:4])
                if decData[:4] == b'Unit':
                    fileExt = "unity3d"
                    open("temp/tempUnity", "wb").write(decData)
                    try:
                        os.makedirs(path)
                    except FileExistsError:
                        pass
                    try:
                        unityBundle = UnityAssetBundle(path)
                        unityBundle.setBundleByPath("temp/tempUnity")
                        unityBundle.extractAssets()
                        i+=1
                        continue
                    except Exception:
                        pass
                    
                elif decData[1:4] == b'PNG':
                    fileExt = "png"
                elif decData[:4] == b'\xff\xd8\xff\xdb':
                    fileExt = "jpg"
                else:
                    fileExt = "bin"
                #  base64.b64encode(fileData[4].encode("utf-8")).decode("utf-8").replace("/", "_BACK_")
                open(
                    "%s/%i.%s" % 
                    (path,i, fileExt), "wb"
                    ).write(decData)
                i+=1