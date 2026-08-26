# =============================================================
# CONFIG — this is the only file you should need to edit by hand
# to add/remove games, groups, ranks, or accounts later.
# =============================================================

# ---- Games to watch for new badges + updates ----
# (placeId is the number from the roblox.com/games/<placeId>/... URL)
GAME_PLACE_IDS = [
    12331228586, 14578124274, 15770515753, 13266544419, 8884517338,
    12845933776, 8484552703, 12827020545, 131882775, 15112416440,
    12439903047, 6561580259, 11882404451, 14356750620, 14418215081,
    11092629813, 14041138292, 9031392986, 15873364494, 7024850757,
    11223054260, 13150335450, 11947050432, 11436601121, 11359659664,
    11230271038, 7789786384, 245038363, 7823978805, 14546260033,
    6410495037, 6385970423, 4223415434, 621325634, 11697013556,
    5029665982, 12743139922, 12966761894, 3191197326, 8024555323,
    121498311, 8646044955, 5959907235, 14034683097, 83874771,
    4096186794, 14277108399, 6185593994, 5011157032, 5601319996,
    7128883469, 7147569629, 102204680843445, 3553571107, 3534290509,
    12534241208, 2762241498, 9606956905, 17129920404, 5419681982,
    12618656793, 15441207007, 13515642399, 3013994145, 5177566708,
    11878289760, 3524117045, 4858720864, 9691219876, 16539811825,
    5208836984, 134371823468430, 134437421868357, 116418281002518,
    90012985721150, 140666962064711, 16061034620, 90043248977642,
    78114747472964, 112396960499297, 5755452223, 2385719796,
    1273270463, 7634189766, 2292774833, 1309858629, 597125580,
    751408477, 2286485880, 95941634, 150470833, 3800900840,
    9823109450, 14046961725, 8904191280, 9277278730, 106165877095010,
    13947740435, 105555476192048, 16119191055, 108378640971562,
    8899336341, 15500992481, 17875192682, 16529500692, 8793592971,
    7630414489, 18250128060, 121688632073304, 111490998558484,
    88888755, 375807536, 15453303673, 88461642144974, 7038244395,
    12960116279, 4463100972, 14001835938,
]

# ---- Specific badge IDs to watch directly (not tied to a tracked game) ----
# The bot watches how many people have earned each one; if that count ticks
# up, it alerts you (useful for a rare/secret badge, e.g. tells you someone
# just found it).
EXTRA_BADGE_IDS = []

# ---- Specific user IDs to watch for "coming online" (added by profile link,
# not username, so these never break if the account renames) ----
EXTRA_USER_IDS = []

# ---- Roblox usernames to watch for "coming online" ----
WATCH_USERNAMES = [
    "Fodloca", "SN00TZ", "Sigillaria", "CAROLlNE", "Z00ZY_Q", "CLlNTEN",
    "MYGAL0", "SPlNNERETTE", "G0Z", "Mulberries", "DrMosen", "TwistedThorey",
    "DISM0L", "Funnycomedians1", "Relazus", "Muzarn", "DaxHaskett", "Jewk",
    "Daelron", "Ipiprix", "Clerince", "Old_Thoughts", "TheSecretarey2",
    "Zergred", "Sakurism", "DavidCult", "JasonCult", "MerleCult", "JimiCult",
    "JoshuaCult", "WillCult", "NickCult", "EmmettCult", "JackCult",
    "TheForgottenScholar", "AkaManah", "RabbitRevenge", "NothingIsOnAccident",
    "RobertSmiles", "DanStickman", "SethSmiIes", "MatthewJSmiles",
    "ClairJSmiles", "LemonB0yy",
]

# ---- Groups + exact rank names to watch for new members ----
# groupId -> list of role names (must match the role name on Roblox exactly)
GROUPS = {
    619142: {
        "name": "Robloxian Myth Hunters",
        "roles": [
            "-[Myth Emeritus]-",
            "-[Established Myth]-",
            "-[Proficient Myth]-",
            "-[Acclaimed Myth]-",
            "-[Myth Legend]-",
        ],
    },
    4311527: {
        "name": "RMH Myth Development",
        "roles": [
            "Myth in Development",
            "Upcoming Myth",
            "Adept Myth",
            "Qualified Myth",
            "Myth Veteran",
        ],
    },
    10218177: {
        "name": "Banana Myths",
        "roles": [
            "Legacy Myth",
            "Developing Myth",
            "Myth",
            "Amazing Myth",
            "Astounding Myth",
        ],
    },
    33083768: {
        "name": "Roblox Myths 2",
        "roles": [
            ":Beginner Myths:",
            ":Small Myths:",
            ":Growing Myths:",
            ":Popular Myths:",
        ],
    },
    36037522: {
        "name": "ANTIQUES MYTHS",
        "roles": [
            "Noticed Myths",
            "Well-Known Myths",
            "Established Myths",
            "Impressive Myths",
        ],
    },
    732128479: {
        "name": "Kylos Myth Directive",
        "roles": [
            "Lesser Myth",
            "Established Myth",
            "Notable Myth",
            "Etched Myth",
        ],
    },
}

# If a tracked game gets a new badge or an update, its owner is
# automatically added to the "online" watchlist too (in addition to
# WATCH_USERNAMES above). This is saved in state.json, not here.
AUTO_WATCH_GAME_OWNERS = True
