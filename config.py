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
    5208836984, 134371823468430, 116418281002518,
    90012985721150, 140666962064711, 16061034620, 90043248977642,
    78114747472964, 112396960499297, 5755452223, 2385719796,
    1273270463, 7634189766, 2292774833, 1309858629, 597125580,
    751408477, 2286485880, 95941634, 150470833, 3800900840,
    9823109450, 14046961725, 8904191280, 9277278730, 106165877095010,
    13947740435, 105555476192048, 16119191055, 108378640971562,
    8899336341, 15500992481, 17875192682, 16529500692, 8793592971,
    7630414489, 18250128060, 121688632073304, 111490998558484,
    5620453624, 375807536, 15453303673, 88461642144974, 7038244395,
    12960116279, 4463100972, 14001835938, 4892161191, 2503371435,
    316624534, 4746308994, 3161352649, 2983623754, 96923836994493,
    12141611336, 14619285685, 2011273269, 2065821410, 6069595082,
    2986558181, 5567471806, 9041405753, 2610191817, 18435782607,
    12994826267, 71591683104334, 9009139090, 13273713934, 13275045990,
    4360483134, 127669292683496, 10536632997,
    9090640493, 16853615558, 15039147264, 17429324487, 7407349577,
    726982743, 2485519908, 5162593998,
    134437421868357, 96362279905097, 10263084449,
    124103375226747, 6638313456, 7894728224, 2282035214,
    6158980553, 4613344486, 109014856986043, 110968355025169,
    2760072732, 5914603929, 545218392, 2652063892,
    104028046593334, 3076458173, 8779505472, 5438372456,
    8723723035, 4928564114, 4837722087, 7206075214,
    9821692221, 2984143514, 3045116449, 3146239190,
    14019924766, 14331280084, 2083625286, 1986335212,
    1014425358, 7293974396, 2554748629, 2108041545,
    1744883151, 1849333870, 1527547100, 4607755796,
    6345467211, 8178737721, 2599634601, 2694168495,
    4504289024, 736134034, 2241571193, 2129310290,
    5166310385, 85359379, 7385645669, 5147915389,
    6447891394, 3578973735, 3657858508,
    3606922055, 4867003179, 2971224109, 2394660488,
   2254302252, 4307361852, 2847189102, 1689306210,
    1375825845, 1690735538, 1431282186, 2847188025,
    2661814904, 2146497378, 1835515224, 2771767457,
    3292113610, 2297532869, 18595639123, 2248490815,
    2090741557, 2295199662, 2133796937, 551385480,
    1867977660, 2141596506, 2200855754, 14350522362,
    2856403528, 932950331, 2036454120, 130156561830927,
    1945722460, 2680712633, 2816979309, 2039217524,
    177249727, 18837727114, 17211136841, 2982876906,
    1380512814, 4597488070, 1986206730, 1295012353,
    1508279593, 1546405486, 1626089720, 997873742,
    1396887447, 262228557, 92718123, 92709051,
    85431136, 87615605, 11895828917, 4531020865,
    6439586781, 45447861, 10272650670, 10293043691
    
    
]

# ---- Specific badge IDs to watch directly (not tied to a tracked game) ----
# The bot watches how many people have earned each one; if that count ticks
# up, it alerts you (useful for a rare/secret badge, e.g. tells you someone
# just found it).
EXTRA_BADGE_IDS = [2124693784]

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
    "ClairJSmiles", "LemonB0yy", "AscendentOne", "Osimker", "HeadOfTaCo",
    "therulerofnothing", "Littlenathanial", "Bobbys_Here", "MrRealism",
    "Taupea", "holovilleMentor", "ColorlessOvercast", "Orenen", "Valorna",
    "LenzCult", "MalegTheDestructor", "T0PSI", "BobbyCult", "DonCult",
    "GrandpaCult", "Antharkhot"
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
