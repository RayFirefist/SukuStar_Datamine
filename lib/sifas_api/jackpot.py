import base64
from lib.sifas_api.constants import VERSION_CONSTANTS_JP

def i32(inp):
    return inp & 0xFFFFFFFF
def i8(inp):
    return inp & 0xFF

class JackpotCore:
    def __init__(self, arch="arm64", VERSION_CONSTANTS=VERSION_CONSTANTS_JP):
        self.arch = arch
        self.PackageSignatures = [
            "3f45f90cbcc718e4b63462baeae90c86",
            "1be2103a6929b38798a29d89044892f3b3934184",
            "1d32dbcf91697d46594ad689d49bb137f65d4bb8f56a26724ae7008648131b82"
        ]
        if arch == "arm":
            raise Exception("arch not updated")
            self.JackpotSignatures = [
                "81ec95e20a695c600375e3b8349722ab",
                "5a3cb86aa9b082d6a1c1dfa6f73dd431d7f14e18",
                "66370b8c96de7266b02bfe17e696d8a61b587656a34b19fbb0b2768a5305dd1d"
            ]
            self.Il2CppSignatures = [
                "67f969e32c2d775b35e2f2ad10b423c1",
                "c4387c429c50c4782ab3df409db3abcfa8fadf79",
                "d30568d1057fecb31a16f4062239c1ec65b9c2beab41b836658b637dcb5a51e4"
            ]
        elif arch == "arm64":
            self.JackpotSignatures = VERSION_CONSTANTS['JackpotSignatures']
            self.Il2CppSignatures = VERSION_CONSTANTS['Il2CppSignatures']
        elif arch == "macho64":
            self.DylibSignatures = [
                "9e0362ab80c1acd44ee8c7fd37688771",
                "9870919b2cff3356872ed337d4ee8af6721a3123",
                "1de3ede8821fd4598fce4e2b066dfd69c462f226a115963e736a31144f09bfa8"
            ]
            self.SegmentSignatures = [
                "f8d0be12cc16f50da5ba47e376e36f69",
                "f1a971152a8a0eecc3d9a08df39aff46249fcdfd",
                "d987c3cbf0d4716dc07feb46aee878973af3d9dd2f70e23dc354a4b4f318b563"
            ]
        else:
            raise Exception("Unknown arch")

    def xor(self, a, b):
        if type(a) == str:
            a = bytes(a, encoding="utf8")
        if type(b) == str:
            b = bytes(b, encoding="utf8")
        result = bytearray()
        for i in range(len(a)):
            result.append(a[i] ^ b[i])
        return result

    def AssetStateLogGenerateV2(self, randomBytes64):
        libHashChar = (randomBytes64[0] & 1) + 1
        libHashType = randomBytes64[libHashChar] % 3
        pkgHashChar = 2 - (randomBytes64[0] & 1)
        pkgHashType = randomBytes64[pkgHashChar] % 3
        if self.arch in ["arm", "arm64"]:
            xoredHashes = self.xor(
                bytearray.fromhex(self.JackpotSignatures[libHashType]),
                bytearray.fromhex(self.Il2CppSignatures[libHashType])
            ).hex()
            packageSignature = self.PackageSignatures[pkgHashType]
        else:
            packageSignature = self.DylibSignatures[pkgHashType]
            xoredHashes = self.SegmentSignatures[libHashType]

        if (randomBytes64[0] & 1) == 0:
            signatures = "{}-{}".format(xoredHashes, packageSignature)
        else:
            signatures = "{}-{}".format(packageSignature, xoredHashes)
        #print("Signat: " + signatures)

        xorkey = (
                         randomBytes64[0] |
                         randomBytes64[1] << 8 |
                         randomBytes64[2] << 16 |
                         randomBytes64[3] << 24
                 ) ^ 0x12d8af36

        a = 0
        b = 0
        c = 0x2bd57287
        d = 0
        e = 0x202c9ea2
        f = 0
        g = 0x139da385
        h = 0
        i = 0
        j = 0
        k = 0

        '''v37 = 0x202c9ea2
        v38 = 0x139da385
        v39 = 0x2bd57287'''

        for index in range(10):
            '''v40 = xorkey ^ i32(xorkey << 11)
            xorkey = v37
            v37 = v38
            v38 = v39
            v39 ^= (v39 >> 19) ^ v40 ^ (v40 >> 8)
            print(xorkey)'''

            h = g
            i = f
            j = e
            k = d
            g = c
            f = b

            a = i32(i32((i32(a << 11) | i32(xorkey >> 21))) ^ a)
            xorkey = i32(i32(xorkey << 11) ^ xorkey)
            c = i32(i32(i32(g >> 19) | i32(k << 13)) ^ xorkey ^ g ^ i32(i32(xorkey >> 8) | i32(a << 24)))
            d = i32(i32(i32(k >> 19) ^ a) ^ k ^ i32(a >> 8))

            xorkey = j
            a = i
            b = k
            e = h
            #print(xorkey)

        xorBytes = bytearray(len(signatures))
        for index in range(len(signatures)):
            a = g
            xorkey = f
            b = i32(i32(i32(i << 11) | i32(j >> 21)) ^ i)
            j = i32(i32(j << 11) ^ j)
            e = i32((i32(c >> 19) ^ i32(d << 13)) ^ j ^ c ^ i32(i32(j >> 8) | i32(b << 24)))
            xorBytes[index] = i8(e)
            f = k
            g = c
            k = d
            j = h
            i = xorkey
            c = e
            d = i32(i32(d >> 19) ^ b ^ d ^ i32(b >> 8))
            h = a

        #signatures = base64.b64decode("RursuQWqCeRyV91k+CpTay/c/Cn49hsS/XFjX032N1V/4S/77AvgtxkTcPGCjScdKSZ9OIYDsW4BivKEmsKcqYaeNk/WTkHYIT4GtZ5++dfwqcMwHp48tTklgj9dBrfBVO9x2orIs4nuPMcwGiRbrgCwYamVOKpwvfYahS1oBQi2")
        result = self.xor(signatures, xorBytes)
        return str(base64.b64encode(result), encoding="utf8")