# School Idol Festival All Stars API

Name reference: Blazblue Cross Tag Battle's quote: "Can't escape from crossing fate"

## Installing guide

### Requirements

* Python 3.6

### Install

* Install the dependencies with `install_dependencies.sh` if you have a UNIX environment (like Ubuntu or macOS) or, if you have Windows, run `install_dependencies.bat`
* Run on cmd/bash/zsh `pip install --no-binary unitypack unitypack` for installing unity assets extraction library
* Then run `python createAccount.py` to create a new account.

### Sample commands

#### Calling API and log in with your account

```python
from lib.sifas_api import SifasApi

api = SifasApi()
api.login()
```

#### Retreiving assets bundles URLs from server

```python
# not copying the login procedure so you must have logged before
api.assetGetPackUrl(["aaaa", "bbbb"]) # those are not legit bundle names
```

#### Download all the database files
```python
# not copying the login procedure so you must have logged before
dbList = api.getDbList()
api.downloadDbs(dbList) # everything will be downloaded into 'assets/db'
```

#### Extracting some assets

WARNING: make sure that you already downloaded/updated your database or you won't see new assets or it will occurr into errors!

```python
# not copying the login procedure so you must have logged before
from lib.sifas_db import AssetDumper

assetDumper = AssetDumper(api) # you must provide a SifasApi instance here. You can provide None but expect errors since it can't reach server for downloading the necessary files
assetDumper.extractStillIllus() # extract still illustrations
assetDumper.extractInlineImages() # extract ui images like login bonus, event/gacha banner, tutorial etc
assetDumper.extractCardsAsset() # extract cards images (full, icon)
assetDumper.extractEmblem() # extract titles
assetDumper.extractTrainingMaterial() # extract training materials thumbnails
assetDumper.extractMemberInfo() # extract member info images (autograph, standing, icon and thumbnail)
assetDumper.extractSuit() # extract costumes preview and models (unity3d bundles)
assetDumper.extractAccessory() # extract accessory thumbnails
assetDumper.extractAudio() # extract audio into WAV file
assetDumper.extractAdvScript() # extract scenario script
assetDumper.extractAdvGraphics() # extract scenario graphics (like sprites)
assetDumper.extractLessonAnimation() # extract lesson animation bundles (unity3d bundles)
assetDumper.extractMusicJackets() # extract music jackets and bgs
assetDumper.extractSound(filter="") # extracts the audio files into WAV files. You can provide a filter of which file(s) you wish to process (by default, it's set as "", so ALL files will be processed, around 13k)
```

## TODO LIST

- [X] loginStartup
- [X] login
- [X] download database
- [X] download assets
- [X] decrypt database and assets
- [X] reading database
- [X] extracting assets
- [X] (WIP) assets naming
- [ ] extract correctly unity files
- [X] extract and deal with audio

# Credits

* [esterTion](https://github.com/esterTion) for assets decryptor base script
* CPPO for HCA key
* [Triangle](https://github.com/summertriangle-dev) for acb.py lib
* [Nyagamon](https://github.com/Nyagamon/HCADecoder) for HCA decoder source code.