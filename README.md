# Myth Hunting Bot

Checks, once an hour, for free, with nothing installed on your computer:

- New **badges** or **updates** on your tracked games
- New **members** at specific ranks in your tracked groups
- Tracked accounts (and any game owner whose game just got a badge/update)
  **coming online**

...and posts anything it finds to a Discord channel.

You don't need to know how to code to set this up — just follow the steps
below. It should take about 10 minutes.

## What you need

- A free [GitHub](https://github.com/join) account (just an email + browser)
- The Discord webhook URL you already have for your server

## Setup steps

### 1. Create a new GitHub repository

1. Go to [github.com/new](https://github.com/new)
2. Name it anything, e.g. `myth-hunting-bot`
3. Set it to **Public** (this keeps you comfortably inside GitHub's free
   Actions minutes — Private also works, it just has a monthly minutes cap)
4. Click **Create repository**

### 2. Upload these files

On the new repo's page, click **"Add file" → "Upload files"**, then drag in
every file and folder from this project (including the `.github` folder —
GitHub will sometimes hide it in your file browser; if drag-and-drop skips
it, use "Add file → Create new file" and type the path
`.github/workflows/check.yml` to create it, then paste in the contents).
Commit the upload.

### 3. Add your Discord webhook as a secret

Never put your webhook URL directly in the code — GitHub Secrets keep it
private even in a public repo.

1. In your repo, go to **Settings → Secrets and variables → Actions**
2. Click **New repository secret**
3. Name: `DISCORD_WEBHOOK_URL`
4. Value: paste your webhook URL
5. Click **Add secret**

### 4. Turn it on

1. Go to the **Actions** tab of your repo
2. You should see "Myth Hunting Check" listed — click it
3. Click **"Run workflow"** to trigger it manually the first time (don't
   worry — the very first run won't send any "new" alerts, since it's just
   learning what currently exists; every run after that will report changes)
4. After that, it runs automatically every hour on its own — you don't need
   to do anything

### 5. Check it worked

After the first manual run finishes (takes a few minutes), check the
**Actions** tab — a green checkmark means it worked. Click into the run and
expand "Run bot" to see what it checked. Your `state.json` file in the repo
will also update with a commit each run — that's normal, that's how it
remembers what it's already seen.

## Editing your lists later

Open `config.py` in the repo (click it, then the pencil/edit icon) to add or
remove:

- `GAME_PLACE_IDS` — the number in a game's URL (`roblox.com/games/<this
  number>/...`)
- `WATCH_USERNAMES` — Roblox usernames to watch for coming online
- `EXTRA_USER_IDS` — user IDs (from a profile URL,
  `roblox.com/users/<this number>/profile`) to watch for coming online,
  for when you'd rather track by ID than username
- `EXTRA_BADGE_IDS` — badge IDs (from a badge URL,
  `roblox.com/badges/<this number>/...`) to watch directly; alerts when
  the number of people who've earned it goes up
- `GROUPS` — add a group by its group ID (the number in
  `roblox.com/communities/<this number>/...`) and the exact rank names you
  want alerts for

Save your edit (commit it) and the next hourly run will pick it up
automatically.

## Notes

- If a game's owner is a **group** rather than a person, that owner isn't
  currently added to the online-watch list (a group can't "come online") —
  only individual owners are auto-added.
- Nothing here touches Roblox gameplay or automates your account in any
  way — it only reads public info, so it's fully within Roblox's rules.
