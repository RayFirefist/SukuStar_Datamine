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
# from lib.unity import UnityAssetBundle
# Base64
import base64
# Criware Lib
from lib.hca import AcbCriware

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
            # still illus
            file = open("%stex_still_%i_%i.jpg" % (path, asset[0], asset[1]), "wb")
            file.write(self.extractSingleAssetWithKeys(path="", table="texture", asset_path=asset[2], forceDownload=forceDownload, returnValue=True))
            file.close()

    def extractInlineImages(self, forceDownload=False):
        path = self.assetsPath + "images/inline/"
        mockPath = self.assetsPath + "images/mock_texture/"
        try:
            os.makedirs(path)
        except FileExistsError:
            pass
        try:
            os.makedirs(mockPath)
        except FileExistsError:
            pass
        mc = self.master.cursor()
        ac = self.assets.cursor()
        assets = mc.execute("SELECT id, path FROM m_inline_image").fetchall()
        for asset in assets:
            tempPath = asset[0].split("/")
            tempPath.pop()
            try:
                os.makedirs("%s%s" % (path, "/".join(tempPath)))
            except FileExistsError:
                pass
            print("elaboration inline %s" % asset[0])
            # inline image
            file = open("%s%s.png" % (path, asset[0]), "wb")
            file.write(self.extractSingleAssetWithKeys(path="", table="texture", asset_path=asset[1], forceDownload=forceDownload, returnValue=True))
            file.close()
        assets = mc.execute("SELECT id, path FROM m_texture_mock").fetchall()
        for asset in assets:
            tempPath = asset[0].split("/")
            tempPath.pop()
            try:
                os.makedirs("%s%s" % (mockPath, "/".join(tempPath)))
            except FileExistsError:
                pass
            print("elaboration inline %s" % asset[0])
            # inline image
            file = open("%s%s.png" % (mockPath, asset[0]), "wb")
            file.write(self.extractSingleAssetWithKeys(path="", table="texture", asset_path=asset[1], forceDownload=forceDownload, returnValue=True))
            file.close()

    def extractEmblem(self, forceDownload=False):
        path = self.assetsPath + "images/emblem/"
        try:
            os.makedirs(path)
        except FileExistsError:
            pass
        mc = self.master.cursor()
        ac = self.assets.cursor()
        assets = mc.execute("SELECT id, emblem_asset_path FROM m_emblem").fetchall()
        for asset in assets:
            print("elaboration emblem %i" % asset[0])
            # image
            file = open("%stex_emblem_%i.jpg" % (path, asset[0]), "wb")
            file.write(self.extractSingleAssetWithKeys(path="", table="texture", asset_path=asset[1], forceDownload=forceDownload, returnValue=True))
            file.close()

    def extractTrainingMaterial(self, forceDownload=False):
        path = self.assetsPath + "images/training_material/"
        try:
            os.makedirs(path)
        except FileExistsError:
            pass
        mc = self.master.cursor()
        ac = self.assets.cursor()
        assets = mc.execute("SELECT id, image_asset_path FROM m_training_material").fetchall()
        for asset in assets:
            print("elaboration training material %i" % asset[0])
            # image
            file = open("%stex_training_material_%i.jpg" % (path, asset[0]), "wb")
            file.write(self.extractSingleAssetWithKeys(path="", table="texture", asset_path=asset[1], forceDownload=forceDownload, returnValue=True))
            file.close()

    def extractMemberInfo(self, forceDownload=False):
        path = self.assetsPath + "images/member/"
        try:
            os.makedirs(path)
        except FileExistsError:
            pass
        mc = self.master.cursor()
        ac = self.assets.cursor()
        assets = mc.execute("SELECT id, standing_image_asset_path, autograph_image_asset_path, member_icon_image_asset_path, thumbnail_image_asset_path FROM m_member").fetchall()
        for asset in assets:
            print("elaboration member %i" % asset[0])
            # standing image
            file = open("%stex_member_standing_%i.jpg" % (path, asset[0]), "wb")
            file.write(self.extractSingleAssetWithKeys(path="", table="texture", asset_path=asset[1], forceDownload=forceDownload, returnValue=True))
            file.close()
            # autograph image
            file = open("%stex_member_autograph_%i.jpg" % (path, asset[0]), "wb")
            file.write(self.extractSingleAssetWithKeys(path="", table="texture", asset_path=asset[2], forceDownload=forceDownload, returnValue=True))
            file.close()
            # member_icon image
            file = open("%stex_member_icon_%i.jpg" % (path, asset[0]), "wb")
            file.write(self.extractSingleAssetWithKeys(path="", table="texture", asset_path=asset[3], forceDownload=forceDownload, returnValue=True))
            file.close()
            # thumb image
            file = open("%stex_member_thumbnail_%i.jpg" % (path, asset[0]), "wb")
            file.write(self.extractSingleAssetWithKeys(path="", table="texture", asset_path=asset[4], forceDownload=forceDownload, returnValue=True))
            file.close()

    def extractSuit(self, extractModels:bool=True, forceDownload=True):
        imagePath = self.assetsPath + "images/suit/"
        modelPath = self.assetsPath + "models/suit/"
        try:
            os.makedirs(imagePath)
        except FileExistsError:
            pass
        try:
            os.makedirs(modelPath)
        except FileExistsError:
            pass
        mc = self.master.cursor()
        ac = self.assets.cursor()
        assets = mc.execute("SELECT id, thumbnail_image_asset_path, model_asset_path FROM m_suit").fetchall()
        for asset in assets:
            print("elaboration member %i" % asset[0])
            depIndex = 1
            shaderIndex = 1
            # thumbnail image
            file = open("%stex_suit_thumbnail_%i.jpg" % (imagePath, asset[0]), "wb")
            file.write(self.extractSingleAssetWithKeys(path="", table="texture", asset_path=asset[1], forceDownload=forceDownload, returnValue=True))
            file.close()
            # suit model
            file = open("%ssuit_%i.unity3d" % (modelPath, asset[0]), "wb")
            file.write(self.extractSingleAssetWithKeys(path="", table="member_model", asset_path=asset[2], forceDownload=forceDownload, returnValue=True))
            file.close()
            # dependencies of model
            if extractModels == False:
                continue
            query = "SELECT dependency FROM member_model_dependency WHERE asset_path = \"%s\"" % asset[2].replace('"', '""')
            print(query)
            for dependence in ac.execute(query):
                file = open("%ssuit_dependency_%i_%i.unity3d" % (modelPath, asset[0], depIndex), "wb")
                file.write(self.extractSingleAssetWithKeys(path="", table="shader" if dependence[0] == "§M|" else "member_model", asset_path=dependence[0], forceDownload=forceDownload, returnValue=True))
                file.close
                if dependence[0] == "§M|":
                    print("shaders")
                    query = "SELECT dependency FROM shader_dependency WHERE asset_path = \"§M|\""
                    for shaderDependence in ac.execute(query):
                        file = open("%ssuit_shader_dependency_%i_%i.unity3d" % (modelPath, asset[0], shaderIndex), "wb")
                        file.write(self.extractSingleAssetWithKeys(path="", table="shader", asset_path=shaderDependence[0], forceDownload=forceDownload, returnValue=True))
                        file.close()
                        shaderIndex += 1
                depIndex += 1

    def extractAccessory(self, forceDownload=False):
        path = self.assetsPath + "images/accessory/"
        try:
            os.makedirs(path)
        except FileExistsError:
            pass
        mc = self.master.cursor()
        ac = self.assets.cursor()
        assets = mc.execute("SELECT id, thumbnail_asset_path FROM m_accessory").fetchall()
        for asset in assets:
            print("elaboration accessory %i" % asset[0])
            # inline image
            file = open("%stex_accessory_%i.jpg" % (path, asset[0]), "wb")
            file.write(self.extractSingleAssetWithKeys(path="", table="texture", asset_path=asset[1], forceDownload=forceDownload, returnValue=True))
            file.close()
    
    def extractAudio(self, forceDownload=False):
        path = self.assetsPath + "sound/"
        try:
            os.makedirs(path)
        except FileExistsError:
            pass
        ac = self.assets.cursor()
        assets = ac.execute("SELECT sheet_name, acb_pack_name FROM m_asset_sound").fetchall()
        for asset in assets:
            print("elaboration acb %s" % asset[0])
            self.downloadPacks([asset[1]], forceDownload)
            tempPath = "%s%s/" % (path, asset[0])
            try:
                os.makedirs(tempPath)
            except FileExistsError:
                pass
            tempAcb = AcbCriware(self.packs[asset[1]], tempPath, asset[0])
            tempAcb.processContents()

    def extractAdvScript(self, forceDownload=False):
        path = self.assetsPath + "adv/script/"
        try:
            os.makedirs(path)
        except FileExistsError:
            pass
        mc = self.master.cursor()
        ac = self.assets.cursor()
        assets = ac.execute("SELECT asset_path, pack_name FROM adv_script").fetchall()
        for asset in assets:
            print("elaboration script %s" % asset[0])
            # inline image
            try:
                tempPath = asset[0].split("/")
                tempPath.pop()
                os.makedirs(path + "/".join(tempPath))
            except FileExistsError:
                pass
            file = open("%s/%s.bin" % (path, asset[0]), "wb")
            file.write(self.extractSingleAssetWithKeys(path="", table="adv_script", asset_path=asset[0], forceDownload=forceDownload, returnValue=True))
            file.close()

    def extractAdvGraphics(self, forceDownload=False):
        path = self.assetsPath + "adv/graphics/"
        try:
            os.makedirs(path)
        except FileExistsError:
            pass
        mc = self.master.cursor()
        ac = self.assets.cursor()
        assets = ac.execute("SELECT script_name, idx, resource FROM adv_graphic").fetchall()
        for asset in assets:
            print("elaboration graphic %s" % asset[0])
            # inline image
            try:
                os.makedirs(path + asset[0])
            except FileExistsError:
                pass
            file = open("%s%s/%i.png" % (path, asset[0], asset[1]), "wb")
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
    
    def extractStageEffect(self):
        self.extractAssetsWithKeys("%s/models/stage_effect/" % self.assetsPath, "stage_effect")

    # deprecated
    #def extractMemberModels(self):
    #    self.extractAssetsWithKeys("%s/models/member/" % self.assetsPath, "member_model")

    def extractTimeline(self):
        self.extractAssetsWithKeys("%s/bundles/timeline/navi/" % self.assetsPath, "navi_timeline")
        self.extractAssetsWithKeys("%s/bundles/timeline/live/" % self.assetsPath, "live_timeline")
        self.extractAssetsWithKeys("%s/bundles/timeline/skill/" % self.assetsPath, "skill_timeline")
    
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
                query = "SELECT pack_name FROM %s WHERE asset_path = \"%s\"" % (table, asset_path.replace("\"", '""'))
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
                    query = "SELECT head, size, key1, key2, asset_path FROM %s WHERE pack_name = '%s' AND asset_path = \"%s\"" % (table, bundle, asset_path.replace("\"", '""'))
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
                    self.downloadPacks([bundle], forceDownload)
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
            os.makedirs("temp")
        except FileExistsError:
            pass
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
        # Extraction time
        query = "SELECT head, size, key1, key2, asset_path, pack_name FROM %s" % table
        queryResult = c.execute(query).fetchall()
        print("Count %i" % queryResult.__len__())
        for fileData in queryResult:
                try:
                    self.packs[fileData[5]]
                except KeyError:
                    self.downloadPacks([fileData[5]], True)
                print("File no. %i" % i)
                data = self.packs[fileData[5]][fileData[0]:fileData[0]+fileData[1]]
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
                        #unityBundle = UnityAssetBundle(path)
                        #unityBundle.setBundleByPath("temp/tempUnity")
                        #unityBundle.extractAssets()
                        #i+=1
                        #continue
                        raise Exception
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