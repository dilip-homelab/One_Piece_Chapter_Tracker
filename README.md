# 🏴‍☠️ One Piece Chapter Tracker

A weekend project I built because I got tired of constantly refreshing the TCB Scans website waiting for the latest One Piece chapter to drop.

This little Python script runs quietly in the background on my Raspberry Pi 5, checks the TCB Scans website every few hours, and sends me an email the moment a new chapter shows up. No more refreshing. No more FOMO.

---

## What it does

- Scrapes the [TCB Scans One Piece page](https://tcbonepiecechapters.com/mangas/5/one-piece) for the latest chapter
- Compares it against the last chapter it saw (saved in a local file)
- If it's new → sends an email notification via [Resend](https://resend.com)
- If nothing changed → logs it and moves on
- Runs automatically on a schedule using **cron**

---


## What the notification looks like

When a new chapter drops, you get an email straight to your inbox:
![[One_piece_manga_email.png]]
Clean and simple — just the chapter name, right when it's out.

---

## Why TCB Scans?

TCB Scans translates One Piece from Japanese to English and releases chapters faster than the official sources. So if you want to read it as early as possible, that's the place to go.

---

## Project structure

```
one_piece_manga_tracker/
├── one_piece_tracker.py          # Main script
├── run_tracker.sh                # Shell script that cron calls
├── .env                          # Your secret API key goes here (never commit this!)
├── one_piece_last_seen_chapter.txt  # Auto-created — stores the last seen chapter
├── tracker.log                   # Script output log
├── cron_debug.log                # Cron execution log (useful for debugging)
└── venv/                         # Python virtual environment
```

---

## Requirements

- Python 3
- A free [Resend](https://resend.com) account for sending emails
- A Raspberry Pi (or any Linux machine) with cron available

---

## Setup

### 1. Check Python is installed

```bash
python3 --version
# or
which python3
```

### 2. Clone the repo and go into the folder

```bash
git clone https://github.com/yourusername/one-piece-manga-tracker.git
cd one-piece-manga-tracker
```

### 3. Create a virtual environment

It's good practice to keep Python dependencies isolated per project.

```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install requests beautifulsoup4 resend python-dotenv
```

### 5. Set up your `.env` file

Create a file called `.env` in the project folder:

```
RESEND_API_KEY=your_actual_api_key_here
RECIPIENT_EMAIL=your_email@gmail.com
```

Both your API key and your email address live here — nothing personal is hardcoded in the script itself.

> ⚠️ **Never share or commit this file.** The `.env` is already in `.gitignore` so git will ignore it automatically.

The script loads it all automatically using `python-dotenv` — no manual exporting needed.

### 6. Update the sender address (optional)

The `"from"` address is currently set to `onboarding@resend.dev`, which is Resend's default for testing. Once you have a verified sender domain in Resend, update that line in `one_piece_tracker.py`. Until then it works fine as-is.

---

## Running it manually (test first!)

Always test the script before setting up cron.

```bash
python3 one_piece_tracker.py
```

Check the output — it'll tell you what chapter it found and whether it sent an email.

---

## Setting up the shell script

The shell script is what cron actually calls. It makes sure the script runs from the right folder with the right Python.

Create `run_tracker.sh`:

```bash
#!/bin/bash

echo "cron touched at $(date)" >> /home/YOUR_USERNAME/Documents/one_piece_manga_tracker/cron_debug.log

cd /home/YOUR_USERNAME/Documents/one_piece_manga_tracker || exit 1

/home/YOUR_USERNAME/Documents/one_piece_manga_tracker/venv/bin/python \
/home/YOUR_USERNAME/Documents/one_piece_manga_tracker/one_piece_tracker.py \
>> /home/YOUR_USERNAME/Documents/one_piece_manga_tracker/tracker.log 2>&1

echo "cron finished at $(date)" >> /home/YOUR_USERNAME/Documents/one_piece_manga_tracker/cron_debug.log
```

> Replace `YOUR_USERNAME` with your actual Linux username. You can find the correct path by navigating to the folder and running `pwd`.

Make it executable:

```bash
chmod +x run_tracker.sh
```

Test it manually:

```bash
./run_tracker.sh
```

Then check the log:

```bash
cat tracker.log
```

---

## Automating with cron

Once the shell script works, open your cron schedule:

```bash
crontab -e
```

Add this single line to run the tracker every hour, every day:

```
0 * * * * /home/YOUR_USERNAME/Documents/one_piece_manga_tracker/run_tracker.sh
```

**Cron format explained:**

```
minute  hour  day-of-month  month  day-of-week  command
  0      *        *            *        *         /path/to/run_tracker.sh
```

The `0` in the minute position means "at the top of the hour". The `*` in the hour position means "every hour". So this fires at 1:00, 2:00, 3:00... all 24 hours, every day. One line is all you need.

Verify it was saved:

```bash
crontab -l
```

---

## Debugging cron

If you're not getting emails and the logs aren't updating, cron itself might not be running.

Check its status:

```bash
systemctl status cron
```

Also check the debug log that the shell script writes:

```bash
cat cron_debug.log
```

---

## How the first run works

On the very first run, the script has no previous chapter to compare against. So it just saves whatever the current latest chapter is and doesn't send an email. The next time a new chapter comes out, it'll detect the change and notify you.

---

## Things to keep in mind

- Chapters usually drop on **Thursdays, Fridays, or Saturdays** — but it varies, which is exactly why automation is useful here
- The script is checking a fan translation site (TCB Scans), not an official source
- The `one_piece_last_seen_chapter.txt` file is auto-generated — you don't need to create it
- If the website changes its structure, the scraper might break and need updating

---

## Built with

- [Python 3](https://www.python.org/)
- [Beautiful Soup 4](https://www.crummy.com/software/BeautifulSoup/) — for scraping
- [Requests](https://requests.readthedocs.io/) — for fetching the page
- [Resend](https://resend.com/) — for sending emails
- [python-dotenv](https://pypi.dev/project/python-dotenv/) — for managing the API key safely
- Cron — for scheduling
- Raspberry Pi 5 — always-on home server

---

*Built over a weekend because waiting for One Piece chapters is genuinely painful.*
