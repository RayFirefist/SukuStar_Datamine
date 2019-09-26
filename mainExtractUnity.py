from lib.unity import UnityAssetBundle

unity = UnityAssetBundle("./assets/images/background/")
unity.setBundleByPath("./assets/images/background/0.png")
print(unity.extractAssets())