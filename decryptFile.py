from lib.penguin import decrypt_stream
import zlib

def decrypt(filepath):
    stream = open(filepath, "rb").read()
    output = decrypt_stream(stream, 2066333189, 487366793, 1972074588)
    open(filepath + "-dec.gz", "wb").write(output)
    open(filepath + "-dec", "wb").write(zlib.decompress(output, -zlib.MAX_WBITS))
    pass

decrypt("asset_i_ja_0.db")