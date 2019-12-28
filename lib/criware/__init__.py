#!/usr/bin/python
# CRIWARE HCA/ACB library

import os
import io
import platform

from .acb import UTFTable, TrackList, AFSArchive, wave_type_ftable  # Thanks Triangle

import subprocess

binaries = {
    "Darwin": "darwin/hca2wav",
    "Linux": "linux/hca2wav",
    "Windows": "windows/hca2wav.exe"
}

class AcbCriware:
    def __init__(self, acb_bytes, target_dir, name, binPath):
        tempFile = open("temp/tempAcb", "wb")
        print("Written bytes")
        print(tempFile.write(acb_bytes))
        tempFile.close()
        utf = UTFTable(open("temp/tempAcb", "rb"))
        self.cue = TrackList(utf)
        self.data_source = AFSArchive(io.BytesIO(utf.rows[0]["AwbFile"]))
        self.target_dir = target_dir
        self.utf = utf
        self.binPath = binPath

    def processContents(self):
        for track in self.cue.tracks:
            print(track)
            fileType = wave_type_ftable.get(track.enc_type, track.enc_type)
            name = "{0}".format(track.name)
            print("Processing %s" % name)
            if fileType == ".hca":
                name = "{0}{1}".format(track.name, ".wav")
                with open("temp/tempHca", "wb") as hca:
                    print(hca.write(self.data_source.file_data_for_cue_id(track.cue_id)))
                subprocess.call([self.binPath + binaries[platform.system()], "temp/tempHca", "-o", os.path.join(self.target_dir, name)])
                #tempHca = HcaCriware(self.data_source.file_data_for_cue_id(track.wav_id), self.target_dir, name)
                #tempHca.processContent()
            else:
                name = "{0}{1}".format(track.name, fileType)
                with open(os.path.join(self.target_dir, name), "wb") as named_out_file:
                    named_out_file.write(self.data_source.file_data_for_cue_id(track.cue_id))
        pass

class AwbCriware:
    def __init__(self, acb_bytes, awb_bytes, target_dir, name, binPath):
        tempFile = open("temp/tempAcb", "wb")
        print("Written bytes")
        print(tempFile.write(acb_bytes))
        tempFile.close()
        utf = UTFTable(open("temp/tempAcb", "rb"))
        print(utf)
        self.cue = TrackList(utf)
        self.data_source = AFSArchive(io.BytesIO(awb_bytes))
        self.target_dir = target_dir
        self.utf = utf
        self.binPath = binPath

    def processContents(self):
        for track in self.cue.tracks:
            print(track)
            fileType = wave_type_ftable.get(track.enc_type, track.enc_type)
            name = "{0}".format(track.name)
            print("Processing %s" % name)
            if fileType == ".hca":
                name = "{0}{1}".format(track.name, ".wav")
                with open("temp/tempHca", "wb") as hca:
                    print(hca.write(self.data_source.file_data_for_cue_id(track.cue_id)))
                subprocess.call([self.binPath + binaries[platform.system()], "temp/tempHca", "-o", os.path.join(self.target_dir, name)])
                # with open(os.path.join(self.target_dir, name), "wb") as named_out_file:
                #     print(named_out_file.write(self.data_source.file_data_for_cue_id(track.wav_id)))
                #tempHca = HcaCriware(self.data_source.file_data_for_cue_id(track.wav_id), self.target_dir, name)
                #tempHca.processContent()
            else:
                name = "{0}{1}".format(track.name, fileType)
                with open(os.path.join(self.target_dir, name), "wb") as named_out_file:
                    named_out_file.write(self.data_source.file_data_for_cue_id(track.cue_id))
        pass
