
"""
Roblox Myth-Hunting Bot
=======================
Checks, once per run:
  1. Tracked games -> new badges + game updates
  2. Watched usernames + IDs -> who just came online
  3. Game owners -> automatically added to online monitoring

Sends notifications to Discord and saves state in state.json.

Failed Discord notifications remain queued for future attempts.
The same successfully announced event cannot be announced again
within 30 minutes.
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
SESSION.headers.update({
    "User-Agent": "myth-hunting-bot/2.0"
})

REQUEST_DELAY = 0.4
ALERT_COOLDOWN_MINUTES = 30
MAX_RETRIES = 3


# =============================================================
# HTTP HELPERS
# =============================================================

def request_with_retry(method, url, **kwargs):
    """Perform an HTTP request with retry and rate-limit handling."""

    for attempt in range(MAX_RETRIES):
        try:
            response = SESSION.request(
                method,
                url,
                timeout=20,
                **kwargs
            )

            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After")

                try:
                    delay = float(retry_after)
                except (ValueError, TypeError):
                    delay = 2 + attempt * 2

                print(f"Rate limited. Waiting {delay} seconds.")
                time.sleep(delay)
                continue

            if response.status_code >= 500:
                print(
                    f"Server error {response.status_code}: {url}"
                )
                time.sleep(1 + attempt)
                continue

            return response

        except requests.RequestException as error:
            print(f"Request failed: {error}")
            time.sleep(1 + attempt)

    print(f"Request permanently failed: {url}")
    return None


def get_json(url, **kwargs):
    """GET JSON from an API."""

    response = request_with_retry("GET", url, **kwargs)

    if response is None or response.status_code != 200:
        return None

    try:
        return response.json()
    except ValueError:
        print(f"Invalid JSON response: {url}")
        return None


def post_json(url, payload):
    """POST JSON to an API."""

    response = request_with_retry(
        "POST",
        url,
        json=payload
    )

    if response is None:
        return None

    if response.status_code not in (200, 201):
        return None

    try:
        return response.json()
    except ValueError:
        return {}


# =============================================================
# STATE
# =============================================================

def load_state():

    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                state = json.load(f)

        except (json.JSONDecodeError, OSError):
            print("WARNING: Could not read state.json.")
            state = {}

    else:
        state = {}

    required_sections = {
        "place_to_universe": {},
        "game_badges": {},
        "game_updated": {},
        "user_ids": {},
        "user_online": {},
        "dynamic_watch_users": {},
        "badge_award_counts": {},
        "extra_user_names": {},
        "alert_cooldowns": {},
        "pending_alerts": []
    }

    for key, default in required_sections.items():
        state.setdefault(key, default)

    # Ensure pending alerts have the expected structure.
    if not isinstance(state["pending_alerts"], list):
        state["pending_alerts"] = []

    return state


def save_state(state):

    temporary_file = STATE_FILE + ".tmp"

    with open(temporary_file, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

    os.replace(temporary_file, STATE_FILE)


def now_iso():
    return datetime.now(timezone.utc).isoformat()


# =============================================================
# ALERT QUEUE AND COOLDOWNS
# =============================================================

def enqueue_alert(state, alert_key, title, line):
    """
    Add an alert to the persistent queue.

    An event is not considered announced until Discord
    successfully accepts its notification.
    """

    cooldowns = state["alert_cooldowns"]

    previous = cooldowns.get(alert_key)

    if previous:
        try:
            previous_time = datetime.fromisoformat(previous)

            if previous_time.tzinfo is None:
                previous_time = previous_time.replace(
                    tzinfo=timezone.utc
                )

            age = datetime.now(timezone.utc) - previous_time

            if age < timedelta(minutes=ALERT_COOLDOWN_MINUTES):
                return

        except (ValueError, TypeError):
            pass

    # Don't queue the same event more than once.
    for pending in state["pending_alerts"]:
        if pending.get("key") == alert_key:
            return

    state["pending_alerts"].append({
        "key": alert_key,
        "title": title,
        "line": line
    })


def send_discord_message(content):
    """Send a Discord message and confirm successful delivery."""

    if not WEBHOOK_URL:
        return False

    response = request_with_retry(
        "POST",
        WEBHOOK_URL,
        json={
            "content": content,
            "allowed_mentions": {
                "parse": []
            }
        }
    )

    if response is None:
        return False

    if response.status_code in (200, 204):
        return True

    print(
        f"Discord delivery failed: HTTP {response.status_code}"
    )

    return False


def deliver_pending_alerts(state):
    """
    Deliver queued notifications.

    Successfully delivered alerts are removed from the queue
    and receive their cooldown timestamp.

    Failed notifications remain queued.
    """

    if not state["pending_alerts"]:
        return

    if not WEBHOOK_URL:
        print("Discord webhook missing. Alerts remain queued.")
        return

    titles = []

    for alert in state["pending_alerts"]:
        if alert["title"] not in titles:
            titles.append(alert["title"])

    for title in titles:

        matching = [
            alert
            for alert in state["pending_alerts"]
            if alert["title"] == title
        ]

        chunks = []
        current_chunk = []

        for alert in matching:

            line = alert["line"]

            # Keep messages comfortably below Discord's limit.
            if current_chunk and (
                sum(len(a["line"]) + 1 for a in current_chunk)
                + len(line) > 1700
            ):
                chunks.append(current_chunk)
                current_chunk = []

            current_chunk.append(alert)

        if current_chunk:
            chunks.append(current_chunk)

        for chunk in chunks:

            content = (
                f"**{title}**\n"
                + "\n".join(a["line"] for a in chunk)
            )

            success = send_discord_message(content)

            if not success:
                print(
                    f"Failed to deliver {len(chunk)} alert(s). "
                    "They will be retried."
                )
                continue

            delivered_keys = {
                alert["key"] for alert in chunk
            }

            for alert in chunk:
                state["alert_cooldowns"][alert["key"]] = now_iso()

            state["pending_alerts"] = [
                alert
                for alert in state["pending_alerts"]
                if alert["key"] not in delivered_keys
            ]

            # Persist each successful delivery immediately.
            save_state(state)

            print(f"Delivered {len(chunk)} alert(s).")

            time.sleep(1)


# =============================================================
# 1. GAMES: BADGES + UPDATES
# =============================================================

def resolve_universe_id(place_id, state):

    key = str(place_id)

    if key in state["place_to_universe"]:
        return state["place_to_universe"][key]

    data = get_json(
        f"https://apis.roblox.com/universes/v1/places/"
        f"{place_id}/universe"
    )

    time.sleep(REQUEST_DELAY)

    if data and "universeId" in data:

        universe_id = data["universeId"]

        state["place_to_universe"][key] = universe_id

        return universe_id

    return None


def fetch_all_game_badges(universe_id):
    """
    Retrieve every badge belonging to a game.

    Returns:
        list: Successfully retrieved badges.
        None: If any page fails.
    """

    badges = []
    cursor = None
    seen_cursors = set()

    while True:

        params = {
            "limit": 100,
            "sortOrder": "Desc"
        }

        if cursor:
            params["cursor"] = cursor

        data = get_json(
            f"https://badges.roblox.com/v1/universes/"
            f"{universe_id}/badges",
            params=params
        )

        time.sleep(REQUEST_DELAY)

        if not data or "data" not in data:
            return None

        badges.extend(data["data"])

        cursor = data.get("nextPageCursor")

        if not cursor:
            break

        # Prevent an accidental infinite pagination loop.
        if cursor in seen_cursors:
            print(f"Repeated badge cursor for game {universe_id}.")
            return None

        seen_cursors.add(cursor)

    return badges


def check_games(state):

    game_ids = list(dict.fromkeys(config.GAME_PLACE_IDS))

    universe_ids = []

    # Resolve universe IDs.
    for place_id in game_ids:

        uid = resolve_universe_id(place_id, state)

        if uid and uid not in universe_ids:
            universe_ids.append(uid)

    # Fetch game information in chunks of 50.
    game_info = {}

    for i in range(0, len(universe_ids), 50):

        chunk = universe_ids[i:i + 50]

        ids_param = ",".join(str(uid) for uid in chunk)

        data = get_json(
            "https://games.roblox.com/v1/games",
            params={
                "universeIds": ids_param
            }
        )

        time.sleep(REQUEST_DELAY)

        if data and "data" in data:

            for game in data["data"]:
                game_info[game["id"]] = game

    new_owner_watches = []

    for uid in universe_ids:

        info = game_info.get(uid)

        if not info:
            continue

        name = info.get("name", f"Universe {uid}")
        updated = info.get("updated")

        creator = info.get("creator") or {}

        creator_id = creator.get("id")
        creator_name = creator.get("name")
        creator_type = creator.get("type")

        key = str(uid)

        game_changed = False

        # -----------------------------------------------------
        # Game update check
        # -----------------------------------------------------

        previous_updated = state["game_updated"].get(key)

        if (
            previous_updated is not None
            and updated
            and updated != previous_updated
        ):

            root_place_id = info.get("rootPlaceId")

            if root_place_id:
                game_url = (
                    f"https://www.roblox.com/games/{root_place_id}"
                )
            else:
                game_url = (
                    f"https://www.roblox.com/games/{uid}"
                )

            enqueue_alert(
                state,
                f"game_update:{uid}",
                "Game updates / new badges",
                f"🔧 **{name}** was updated (<{game_url}>)"
            )

            game_changed = True

        # Only replace the previous value when a new value exists.
        if updated:
            state["game_updated"][key] = updated

        # -----------------------------------------------------
        # Badge check
        # -----------------------------------------------------

        badge_data = fetch_all_game_badges(uid)

        if badge_data is not None:

            previous_ids = set(
                state["game_badges"].get(key, [])
            )

            current_ids = [
                badge["id"]
                for badge in badge_data
            ]

            new_badges = [
                badge
                for badge in badge_data
                if badge["id"] not in previous_ids
            ]

            # Check whether a baseline already exists.
            # This also handles games whose initial badge list
            # was genuinely empty.
            if key in state["game_badges"]:

                for badge in new_badges:

                    badge_id = badge["id"]

                    badge_name = badge.get(
                        "name",
                        "Unknown"
                    )

                    enqueue_alert(
                        state,
                        f"new_badge:{uid}:{badge_id}",
                        "Game updates / new badges",
                        (
                            f"🏅 New badge in **{name}**: "
                            f"*{badge_name}* "
                            f"(<https://www.roblox.com/badges/"
                            f"{badge_id}>)"
                        )
                    )

                    game_changed = True

            # Only save complete badge results.
            state["game_badges"][key] = current_ids

        # -----------------------------------------------------
        # Automatically watch game owners
        # -----------------------------------------------------

        if (
            game_changed
            and config.AUTO_WATCH_GAME_OWNERS
            and creator_type == "User"
            and creator_id
        ):

            new_owner_watches.append(
                (creator_id, creator_name)
            )

    return new_owner_watches


# =============================================================
# 1B. SPECIFIC STANDALONE BADGES
# =============================================================

def check_extra_badges(state):

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

        if count is None:
            continue

        key = str(badge_id)

        previous = state["badge_award_counts"].get(key)

        if previous is not None and count > previous:

            enqueue_alert(
                state,
                f"extra_badge:{badge_id}",
                "Game updates / new badges",
                (
                    f"🏅 **{name}** was just earned by someone "
                    f"(award count {previous} → {count}) "
                    f"(<https://www.roblox.com/badges/"
                    f"{badge_id}>)"
                )
            )

        state["badge_award_counts"][key] = count


# =============================================================
# 2. ACCOUNT RESOLUTION
# =============================================================

def resolve_usernames(usernames, state):

    missing = [
        username
        for username in usernames
        if username not in state["user_ids"]
    ]

    for i in range(0, len(missing), 100):

        chunk = missing[i:i + 100]

        data = post_json(
            "https://users.roblox.com/v1/usernames/users",
            {
                "usernames": chunk,
                "excludeBannedUsers": False
            }
        )

        time.sleep(REQUEST_DELAY)

        if data and "data" in data:

            for user in data["data"]:

                state["user_ids"][
                    user["requestedUsername"]
                ] = user["id"]


def resolve_extra_user_ids(state):

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


# =============================================================
# 3. ONLINE MONITORING
# =============================================================

def check_online(state, extra_users):

    resolve_usernames(
        config.WATCH_USERNAMES,
        state
    )

    resolve_extra_user_ids(state)

    watch_ids = {}

    # Config usernames.
    for username in config.WATCH_USERNAMES:

        uid = state["user_ids"].get(username)

        if uid:
            watch_ids[int(uid)] = username

    # Directly watched IDs.
    for uid in config.EXTRA_USER_IDS:

        watch_ids[int(uid)] = state[
            "extra_user_names"
        ].get(
            str(uid),
            f"User {uid}"
        )

    # Previously discovered game owners.
    for uid, username in state["dynamic_watch_users"].items():

        try:
            watch_ids[int(uid)] = username
        except (ValueError, TypeError):
            continue

    # Newly discovered game owners.
    for uid, username in extra_users:

        uid = int(uid)

        if uid not in watch_ids:

            watch_ids[uid] = username or f"User {uid}"

            state["dynamic_watch_users"][str(uid)] = (
                username or f"User {uid}"
            )

    all_ids = list(watch_ids.keys())

    # ---------------------------------------------------------
    # Retrieve presence
    # ---------------------------------------------------------

    for i in range(0, len(all_ids), 100):

        chunk = all_ids[i:i + 100]

        data = post_json(
            "https://presence.roblox.com/v1/presence/users",
            {
                "userIds": chunk
            }
        )

        time.sleep(REQUEST_DELAY)

        # If the API fails, preserve previous statuses.
        if not data or "userPresences" not in data:
            print("Presence request failed. Keeping previous statuses.")
            continue

        returned_ids = set()

        for presence in data["userPresences"]:

            uid = int(presence["userId"])
            returned_ids.add(uid)

            # 0 = Offline
            # 1 = Online
            # 2 = InGame
            # 3 = InStudio

            is_online = (
                presence.get("userPresenceType", 0) != 0
            )

            was_online = state["user_online"].get(
                str(uid),
                False
            )

            if is_online and not was_online:

                enqueue_alert(
                    state,
                    f"user_online:{uid}",
                    "Accounts online",
                    (
                        f"🟢 **{watch_ids[uid]}** just came online "
                        f"(<https://www.roblox.com/users/"
                        f"{uid}/profile>)"
                    )
                )

            state["user_online"][str(uid)] = is_online

        # If Roblox omits an ID from a successful response,
        # preserve its previous status rather than assuming offline.
        missing_ids = set(chunk) - returned_ids

        if missing_ids:
            print(
                f"Presence response omitted {len(missing_ids)} "
                "account(s). Their previous statuses were preserved."
            )


# =============================================================
# 4. MAIN
# =============================================================

def main():

    print("=" * 55)
    print("ROBLOX MYTH-HUNTING BOT")
    print("=" * 55)

    if not WEBHOOK_URL:
        print(
            "WARNING: DISCORD_WEBHOOK_URL is not set. "
            "Notifications will remain queued."
        )

    state = load_state()

    print("\nChecking games...")

    new_owner_watches = check_games(state)

    print("\nChecking standalone badges...")

    check_extra_badges(state)

    print("\nChecking online accounts...")

    check_online(
        state,
        new_owner_watches
    )

    # Save discoveries and pending notifications before delivery.
    save_state(state)

    print("\nDelivering pending notifications...")

    deliver_pending_alerts(state)

    pending_count = len(state["pending_alerts"])

    print("\n" + "=" * 55)
    print("CHECK COMPLETE")
    print(f"Pending notifications: {pending_count}")
    print(f"Finished at: {now_iso()}")
    print("=" * 55)


if __name__ == "__main__":
    main()
