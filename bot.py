"""
Roblox Myth-Hunting Bot
=======================
Checks, once per run:
  1. Tracked games -> new badges + game updates (and remembers the owner)
  2. Tracked group ranks -> new members
  3. Watched usernames (+ owners auto-added from #1) -> who just came online

Sends everything it finds to a Discord webhook, then saves what it saw
to state.json so next run only reports NEW stuff.

Alerts for the same exact event are limited to once every 30 minutes.

You should not need to edit this file. Edit config.py to change what's
tracked. See README.md for setup instructions.
"""

import json
import os
import time
from datetime import datetime, timezone, timedelta

import requests
import config


STATE_FILE = "state.json"
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "myth-hunting-bot/1.0"})

REQUEST_DELAY = 0.4  # small pause between calls to be gentle on Roblox's API

# Same exact event cannot be announced more than once during this period.
ALERT_COOLDOWN_MINUTES = 30


# -------------------------------------------------------------------
# small helpers
# -------------------------------------------------------------------

def get_json(url, **kwargs):
    """GET a URL and return parsed JSON, with basic retry on failure."""
    for attempt in range(3):
        try:
            resp = SESSION.get(url, timeout=15, **kwargs)

            if resp.status_code == 200:
                return resp.json()

            if resp.status_code == 429:
                time.sleep(2 + attempt * 2)
                continue

            return None

        except requests.RequestException:
            time.sleep(1 + attempt)

    return None


def post_json(url, payload):
    for attempt in range(3):
        try:
            resp = SESSION.post(url, json=payload, timeout=15)

            if resp.status_code == 200:
                return resp.json()

            if resp.status_code == 429:
                time.sleep(2 + attempt * 2)
                continue

            return None

        except requests.RequestException:
            time.sleep(1 + attempt)

    return None


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            state = json.load(f)

        # Add the cooldown dictionary if this is an older state.json
        # that was created before cooldown support existed.
        if "alert_cooldowns" not in state:
            state["alert_cooldowns"] = {}

        return state

    return {
        "place_to_universe": {},   # placeId -> universeId
        "game_badges": {},         # universeId -> [badgeIds seen]
        "game_updated": {},        # universeId -> last known updated timestamp
        "group_members": {},       # "groupId:roleId" -> [userIds seen]
        "user_ids": {},            # username -> userId
        "user_online": {},         # userId -> True/False (last known state)
        "dynamic_watch_users": {}, # userId -> username, added from game owners
        "badge_award_counts": {},  # badgeId -> last known awardedCount
        "extra_user_names": {},    # userId -> resolved display name

        # alert key -> ISO timestamp of the last time it was announced
        "alert_cooldowns": {},
    }


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def now_iso():
    return datetime.now(timezone.utc).isoformat()


# -------------------------------------------------------------------
# Alert cooldown
# -------------------------------------------------------------------

def should_alert(state, alert_key):
    """
    Return True if this exact alert is allowed to be sent.

    The same alert key can only be announced once every
    ALERT_COOLDOWN_MINUTES minutes.
    """

    cooldowns = state.setdefault("alert_cooldowns", {})

    previous = cooldowns.get(alert_key)

    if previous:
        try:
            previous_time = datetime.fromisoformat(previous)

            # Make sure old timestamps without timezone information
            # don't cause comparison errors.
            if previous_time.tzinfo is None:
                previous_time = previous_time.replace(tzinfo=timezone.utc)

            age = datetime.now(timezone.utc) - previous_time

            if age < timedelta(minutes=ALERT_COOLDOWN_MINUTES):
                return False

        except (ValueError, TypeError):
            # If an old/broken timestamp exists, allow the alert.
            pass

    # Record the time this alert was allowed.
    cooldowns[alert_key] = now_iso()

    return True


# -------------------------------------------------------------------
# Discord
# -------------------------------------------------------------------

def send_to_discord(lines, title):
    """Send a batch of alert lines to Discord, chunked to stay under
    Discord's per-message character limit."""

    if not lines or not WEBHOOK_URL:
        return

    chunk = []
    chunk_len = 0
    chunks = []

    for line in lines:
        if chunk_len + len(line) > 1800:
            chunks.append(chunk)
            chunk = []
            chunk_len = 0

        chunk.append(line)
        chunk_len += len(line)

    if chunk:
        chunks.append(chunk)

    for c in chunks:
        content = f"**{title}**\n" + "\n".join(c)

        post_json(
            WEBHOOK_URL,
            {"content": content}
        )

        time.sleep(1)


# -------------------------------------------------------------------
# 1. Games: badges + updates
# -------------------------------------------------------------------

def resolve_universe_id(place_id, state):
    key = str(place_id)

    if key in state["place_to_universe"]:
        return state["place_to_universe"][key]

    data = get_json(
        f"https://apis.roblox.com/universes/v1/places/{place_id}/universe"
    )

    time.sleep(REQUEST_DELAY)

    if data and "universeId" in data:
        state["place_to_universe"][key] = data["universeId"]
        return data["universeId"]

    return None


def check_games(state):
    alerts = []
    new_owner_watches = []

    # Resolve all universe IDs first
    universe_ids = []

    for place_id in config.GAME_PLACE_IDS:
        uid = resolve_universe_id(place_id, state)

        if uid:
            universe_ids.append(uid)

    # Batch-fetch game info (name, updated time, creator) in chunks of 50
    game_info = {}

    for i in range(0, len(universe_ids), 50):
        chunk = universe_ids[i:i + 50]
        ids_param = ",".join(str(u) for u in chunk)

        data = get_json(
            f"https://games.roblox.com/v1/games?universeIds={ids_param}"
        )

        time.sleep(REQUEST_DELAY)

        if data and "data" in data:
            for g in data["data"]:
                game_info[g["id"]] = g

    for uid in universe_ids:
        info = game_info.get(uid)

        if not info:
            continue

        name = info.get("name", f"Universe {uid}")
        updated = info.get("updated")

        creator = info.get("creator", {})
        creator_id = creator.get("id")
        creator_name = creator.get("name")
        creator_type = creator.get("type")

        key = str(uid)

        prev_updated = state["game_updated"].get(key)
        game_changed = False

        # -----------------------------------------------------------
        # Game update check
        # -----------------------------------------------------------

        if prev_updated is not None and updated and updated != prev_updated:
            root_place_id = info.get("rootPlaceId")

            game_url = (
                f"https://www.roblox.com/games/{root_place_id}"
                if root_place_id
                else f"https://www.roblox.com/games/{uid}"
            )

            alert_key = f"game_update:{uid}:{updated}"

            if should_alert(state, alert_key):
                alerts.append(
                    f"🔧 **{name}** was updated (<{game_url}>)"
                )

            game_changed = True

        state["game_updated"][key] = updated

        # -----------------------------------------------------------
        # Badges
        # -----------------------------------------------------------

        badge_data = get_json(
            f"https://badges.roblox.com/v1/universes/{uid}/badges"
            f"?limit=100&sortOrder=Desc"
        )

        time.sleep(REQUEST_DELAY)

        if badge_data and "data" in badge_data:
            seen = set(
                state["game_badges"].get(key, [])
            )

            current_ids = [
                b["id"]
                for b in badge_data["data"]
            ]

            new_badges = [
                b for b in badge_data["data"]
                if b["id"] not in seen
            ]

            if seen and new_badges:
                for b in new_badges:

                    alert_key = (
                        f"new_badge:{uid}:{b['id']}"
                    )

                    if should_alert(state, alert_key):
                        alerts.append(
                            f"🏅 New badge in **{name}**: "
                            f"*{b.get('name', 'Unknown')}* "
                            f"(<https://www.roblox.com/badges/{b['id']}>)"
                        )

                    game_changed = True

            state["game_badges"][key] = current_ids

        # -----------------------------------------------------------
        # Auto-add owner to online watchlist if game changed
        # -----------------------------------------------------------

        if (
            game_changed
            and config.AUTO_WATCH_GAME_OWNERS
            and creator_type == "User"
            and creator_id
        ):
            new_owner_watches.append(
                (creator_id, creator_name)
            )

    return alerts, new_owner_watches


# -------------------------------------------------------------------
# 1b. Specific standalone badges
# -------------------------------------------------------------------

def check_extra_badges(state):
    alerts = []

    for badge_id in config.EXTRA_BADGE_IDS:
        data = get_json(
            f"https://badges.roblox.com/v1/badges/{badge_id}"
        )

        time.sleep(REQUEST_DELAY)

        if not data:
            continue

        name = data.get(
            "name",
            f"Badge {badge_id}"
        )

        count = data.get(
            "statistics",
            {}
        ).get("awardedCount")

        key = str(badge_id)

        prev = state["badge_award_counts"].get(key)

        if (
            prev is not None
            and count is not None
            and count > prev
        ):
            alert_key = (
                f"extra_badge:{badge_id}:{count}"
            )

            if should_alert(state, alert_key):
                alerts.append(
                    f"🏅 **{name}** was just earned by someone "
                    f"(award count {prev} → {count}) "
                    f"(<https://www.roblox.com/badges/{badge_id}>)"
                )

        if count is not None:
            state["badge_award_counts"][key] = count

    return alerts


# -------------------------------------------------------------------
# 2. Groups: new members at watched ranks
# -------------------------------------------------------------------

def check_groups(state):
    alerts = []

    for group_id, group_cfg in config.GROUPS.items():

        roles_data = get_json(
            f"https://groups.roblox.com/v1/groups/{group_id}/roles"
        )

        time.sleep(REQUEST_DELAY)

        if not roles_data or "roles" not in roles_data:
            continue

        wanted = set(group_cfg["roles"])

        for role in roles_data["roles"]:

            if role["name"] not in wanted:
                continue

            role_id = role["id"]
            key = f"{group_id}:{role_id}"

            members = []
            cursor = ""

            for _ in range(50):
                url = (
                    f"https://groups.roblox.com/v1/groups/{group_id}"
                    f"/roles/{role_id}/users"
                    f"?limit=100&cursor={cursor}"
                )

                data = get_json(url)

                time.sleep(REQUEST_DELAY)

                if not data or "data" not in data:
                    break

                members.extend(
                    u["userId"]
                    for u in data["data"]
                )

                cursor = data.get("nextPageCursor")

                if not cursor:
                    break

            prev_members = set(
                state["group_members"].get(key, [])
            )

            new_members = [
                m
                for m in members
                if m not in prev_members
            ]

            if prev_members and new_members:

                for uid in new_members:

                    alert_key = (
                        f"group_member:{group_id}:{role_id}:{uid}"
                    )

                    if should_alert(state, alert_key):
                        alerts.append(
                            f"⭐ New **{role['name']}** in "
                            f"*{group_cfg['name']}*: "
                            f"<https://www.roblox.com/users/{uid}/profile>"
                        )

            state["group_members"][key] = members

    return alerts


# -------------------------------------------------------------------
# 3. Accounts: who just came online
# -------------------------------------------------------------------

def resolve_usernames(usernames, state):
    """Fill in state['user_ids'] for any usernames we haven't resolved yet."""

    missing = [
        u
        for u in usernames
        if u not in state["user_ids"]
    ]

    for i in range(0, len(missing), 100):

        chunk = missing[i:i + 100]

        data = post_json(
            "https://users.roblox.com/v1/usernames/users",
            {
                "usernames": chunk,
                "excludeBannedUsers": False
            },
        )

        time.sleep(REQUEST_DELAY)

        if data and "data" in data:

            for u in data["data"]:
                state["user_ids"][
                    u["requestedUsername"]
                ] = u["id"]


def resolve_extra_user_ids(state):
    """Fill in display names for config.EXTRA_USER_IDS."""

    for uid in config.EXTRA_USER_IDS:

        key = str(uid)

        if key in state["extra_user_names"]:
            continue

        data = get_json(
            f"https://users.roblox.com/v1/users/{uid}"
        )

        time.sleep(REQUEST_DELAY)

        if data and "name" in data:
            state["extra_user_names"][key] = data["name"]
        else:
            state["extra_user_names"][key] = f"User {uid}"


def check_online(state, extra_users):
    alerts = []

    resolve_usernames(
        config.WATCH_USERNAMES,
        state
    )

    resolve_extra_user_ids(state)

    watch_ids = {}

    # Usernames
    for uname in config.WATCH_USERNAMES:

        uid = state["user_ids"].get(uname)

        if uid:
            watch_ids[uid] = uname

    # Directly-watched user IDs
    for uid in config.EXTRA_USER_IDS:

        watch_ids[uid] = state[
            "extra_user_names"
        ].get(
            str(uid),
            f"User {uid}"
        )

    # Dynamically-added game owners
    for uid, uname in state[
        "dynamic_watch_users"
    ].items():

        watch_ids[int(uid)] = uname

    # Newly discovered owners
    for uid, uname in extra_users:

        if uid not in watch_ids:

            watch_ids[uid] = uname

            state[
                "dynamic_watch_users"
            ][str(uid)] = uname

    all_ids = list(watch_ids.keys())

    online_now = set()

    for i in range(0, len(all_ids), 100):

        chunk = all_ids[i:i + 100]

        data = post_json(
            "https://presence.roblox.com/v1/presence/users",
            {"userIds": chunk}
        )

        time.sleep(REQUEST_DELAY)

        if data and "userPresences" in data:

            for p in data["userPresences"]:

                # 0 = Offline
                # 1 = Online
                # 2 = InGame
                # 3 = InStudio

                if p.get(
                    "userPresenceType",
                    0
                ) != 0:

                    online_now.add(
                        p["userId"]
                    )

    for uid in all_ids:

        was_online = state[
            "user_online"
        ].get(
            str(uid),
            False
        )

        is_online = uid in online_now

        if is_online and not was_online:

            alert_key = f"user_online:{uid}"

            if should_alert(
                state,
                alert_key
            ):
                alerts.append(
                    f"🟢 **{watch_ids[uid]}** just came online "
                    f"(<https://www.roblox.com/users/{uid}/profile>)"
                )

        state[
            "user_online"
        ][str(uid)] = is_online

    return alerts


# -------------------------------------------------------------------
# main
# -------------------------------------------------------------------

def main():

    if not WEBHOOK_URL:
        print(
            "WARNING: DISCORD_WEBHOOK_URL is not set — "
            "alerts will be printed only."
        )

    state = load_state()

    print("Checking games...")

    game_alerts, new_owner_watches = check_games(
        state
    )

    print("Checking standalone badges...")

    badge_alerts = check_extra_badges(
        state
    )

    print("Checking groups...")

    group_alerts = check_groups(
        state
    )

    print("Checking online status...")

    online_alerts = check_online(
        state,
        new_owner_watches
    )

    # Save everything, including cooldown timestamps,
    # before sending the Discord messages.
    save_state(state)

    send_to_discord(
        game_alerts + badge_alerts,
        "Game updates / new badges"
    )

    send_to_discord(
        group_alerts,
        "New group members"
    )

    send_to_discord(
        online_alerts,
        "Accounts online"
    )

    total = (
        len(game_alerts)
        + len(badge_alerts)
        + len(group_alerts)
        + len(online_alerts)
    )

    print(
        f"Done. {total} alert(s) sent. "
        f"Run finished at {now_iso()}."
    )


if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
