# School Idol Festival All Stars API

Name reference: Blazblue Cross Tag Battle's quote: "Can't escape from crossing fate"

## Installing guide

### Requirements

* Python 3.6

### Install

* Install the dependencies with `pip install -r requirements` or, if you have Windows, run `install_dependencies.bat`
* Run on cmd/bash/zsh `pip install --no-binary unitypack unitypack` for installing unity assets extraction library


### Sample commands

#### Calling API and making a new account

```python
from lib.sifas_api import SifasApi

api = SifasApi()
api.loginStartUp()
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
```python
# not copying the login procedure so you must have logged before
from lib.sifas_db import AssetDumper

assetDumper = AssetDumper(api) # you must provide a SifasApi instance here. You can provide None but expect errors since it can't reach server for downloading the necessary files
assetDumper.extractBackground() # extract background images
```

## TODO LIST

- [X] loginStartup
- [ ] login
- [X] download database
- [X] download assets
- [X] decrypt database and assets
- [X] reading database
- [X] extracting assets
- [ ] (WIP) assets naming
- [ ] extract correctly unity files
- [ ] extract and deal with audio