from enum import Enum

class SifasEndpoints(Enum):
    ACCESSORY_ALLUNEQUIP = "/accessory/allUnequip"
    ACCESSORY_MELT = "/accessory/melt"
    ACCESSORY_POWERUP = "/accessory/powerUp"
    ACCESSORY_RARITYUP = "/accessory/rarityUp"
    ACCESSORY_UPDATEISNEW = "/accessory/updateIsNew"
    EMBLEM_ACTIVATEEMBLEM = "/emblem/activateEmblem"
    TRAININGTREE_ACTIVATETRAININGTREECELL = "/trainingTree/activateTrainingTreeCell"
    USER_ADDACCESSORYBOXLIMIT = "/user/addAccessoryBoxLimit"
    USERPFOFILE_FETCHPROFILE = "/userProfile/fetchProfile"
    BILLING_APPLEPURCHASE = "/billing/applePurchase"
    FRIEND_APPLY = "/friend/apply"
    FRIEND_APPLYOTHERSCENE = "/friend/applyOtherScene"
    FRIEND_APPROVE = "/friend/approve"
    FRIEND_APPROVEOTHERSCENE = "/friend/approveOtherScene"
    FRIEND_CANCEL = "/friend/cancel"
    FRIEND_CANCELOTHERSCENE = "/friend/cancelOtherScene"
    CAUTION_READ = "/caution/read"
    LESSON_CHANGEDECKNAMELESSONDECK = "/lesson/changeDeckNameLessonDeck"
    LIVEDECK_CHANGEDECKNAMELIVEDECK = "/liveDeck/changeDeckNameLiveDeck"
    CARD_CHANGEFAVORITE = "/card/changeFavorite"
    CARD_ISAWAKENINGIMAGE = "/card/changeIsAwakeningImage"
    LIVEDECK_CHANGENAMELIVEPARTY = "/liveDeck/changeNameLiveParty"
    MISSION_CLEARMISSIONNEWBADGE = "/mission/clearMissionNewBadge"
    SHOP_EXCHANGESHOPEVENTEXCHANGE = "/shop/exchangeShopEventExchange"
    SHOP_EXCHANGESHOPITEMEXCHANGE = "/shop/exchangeShopItemExchange"
    LESSON_EXECUTELESSON = "/lesson/executeLesson"
    BILLING_FETCHBILLINGHISTORY = "/billing/fetchBillingHistory"
    BOOTSTRAP_FETCHBOOTSTRAP = "/bootstrap/fetchBootstrap"
    DATALINK_FETCHDATALINKS = "/dataLink/fetchDataLinks"
    EMBLEM_FETCHEMBLEM = "/emblem/fetchEmblem"

    # Event Marathon
    EVENTMARATHON_FETCHEVENTMARATHON = "/eventMarathon/fetchEventMarathon"
    EVENTMARATHONRANKING_FETCHEVENTMARATHONRANKING = "/eventMarathonRanking/fetchEventMarathonRanking"
    # Event Mining
    EVENTMINING_FETCHEVENTMINING = "/eventMining/fetchEventMining"
    EVENTMININGRANKING_FETCHEVENTMININGRANKING = "/eventMiningRanking/fetchEventMiningRanking"

    FRIEND_FETCHFRIENDLIST = "/friend/fetchFriendList"
    GACHA_FETCHGACHALIST = "/gacha/fetchGachaMenu"
    DATALINK_FETCHGAMESERVICEDATA = "/dataLink/fetchGameServiceData"

    #
    #
    #
    #
    #
    NOTICE_FETCHNOTICE = "/notice/fetchNotice"
    NOTICE_FETCHNOTICEDETAIL = "/notice/fetchNoticeDetail"
    NOTICE_FETCHNOTICELIST = "/notice/fetchNoticeList"
    #
    LOGIN_LOGIN = "/login/login"
    LOGIN_STARTUP = "/login/startup"
    #
    ASSET_GETPACKURL = "/asset/getPackUrl"
    # 
    TERMS_AGREEMENT = "/terms/agreement"