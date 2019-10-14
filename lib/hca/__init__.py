# CRIWARE CLASS

import os
import io

import lib.hca.acb as acb # Thanks Triangle
import hcapy

# HCA Heys
key0 = "0192806D"
key1 = "5A2F6F6F"

class HcaCriware:
    def __init__(self, hca_bytes, target_dir, name, key0=key0, key1=key1):
        tempFile = open("temp/tempHca", "wb")
        tempFile.write(hca_bytes)
        tempFile.close()
        self.decode = hcapy.Decoder(key0, key1)
        self.decode.decode_file("temp/tempHca")
        self.target_dir = target_dir
        self.name = name
        pass

    def processContent(self):
        try:
            with open("target_file.hca", "rb") as f, open("%s/%s" % (self.target_dir, self.name), "wb") as f2:
                f2.write(self.decode.decode(f.read()).read())  # bytesからデコード、io.BytesIOでリターンする
                f2.close()
                f.close()
        except hcapy.InvalidHCAError:
            print("invalid hca!")

class AcbCriware:
    def __init__(self, acb_bytes, target_dir, name):
        tempFile = open("temp/tempAcb", "wb")
        tempFile.write(acb_bytes)
        tempFile.close()
        utf = acb.UTFTable(open("temp/tempAcb", "rb"))
        self.cue = acb.TrackList(utf)
        self.data_source = acb.AFSArchive(io.BytesIO(utf.rows[0]["AwbFile"]))
        self.target_dir = target_dir
        self.utf = utf

    def processContents(self):
        for track in self.cue.tracks:
            print(track)
            fileType = acb.wave_type_ftable.get(track.enc_type, track.enc_type)
            name = "{0}".format(track.name)
            print("Processing %s" % name)
            if fileType == acb.wave_type_ftable['WAVEFORM_ENCODE_TYPE_HCA']:
                tempHca = HcaCriware(self.data_source.file_data_for_cue_id(track.wav_id), self.target_dir, name)
                tempHca.processContent()
            else:
                name = "{0}{1}".format(track.name, fileType)
                with open(os.path.join(self.target_dir, name), "wb") as named_out_file:
                    named_out_file.write()
        pass
