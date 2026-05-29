import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
import os
import resend
from dotenv import load_dotenv
from datetime import datetime


# Load environment variables from the .env file
# This is how we keep secrets like API keys out of the code itself
load_dotenv()

# Set the Resend API key from the environment variable — never hardcode this
resend.api_key = os.environ["RESEND_API_KEY"]

# Your email address, loaded from .env so it's not hardcoded in the script
RECIPIENT_EMAIL = os.environ["RECIPIENT_EMAIL"]

# The TCB Scans page that lists all One Piece chapters
URL = "https://tcbonepiecechapters.com/mangas/5/one-piece"

# This file stores the last chapter we saw, so we can compare on the next run
LAST_FILE = "one_piece_last_seen_chapter.txt"


def log(message):
    """Print a timestamped message to the console (and log file via shell redirect)."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


def get_latest_chapter():
    """
    Scrape the TCB Scans One Piece page and return the title of the latest chapter.
    Returns None if the request fails or no chapters are found.
    """
    # Pretend to be a browser so the site doesn't block us as a bot
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(URL, headers=headers, timeout=15)
        log(f"Status code: {response.status_code}")

        if response.status_code != 200:
            log(f"Failed to fetch page. Status code: {response.status_code}")
            return None

    except RequestException as e:
        # Catch network errors (no internet, timeout, DNS failure, etc.)
        log(f"Network error while fetching chapter page: {e}")
        return None

    # Parse the page HTML
    soup = BeautifulSoup(response.text, "html.parser")

    chapter_links = []

    # Look through every link on the page
    for link in soup.find_all("a", href=True):
        text = link.get_text(" ", strip=True)
        href = link["href"]

        # Only grab links that point to actual One Piece chapter pages
        if "one-piece-chapter" in href.lower() and text:
            chapter_links.append(text)

    # Remove duplicates while keeping the original order
    chapter_links = list(dict.fromkeys(chapter_links))

    if not chapter_links:
        raise Exception("No chapter links found.")

    # The first link on the page is the newest chapter
    latest_chapter = chapter_links[0]
    return latest_chapter


def load_last_seen():
    """
    Read the last seen chapter from the saved file.
    Returns None if the file doesn't exist yet (first run).
    """
    if os.path.exists(LAST_FILE):
        with open(LAST_FILE, "r", encoding="utf-8") as file:
            return file.read().strip()
    return None


def save_last_seen(chapter_name):
    """Save the current latest chapter to file so we remember it next run."""
    with open(LAST_FILE, "w", encoding="utf-8") as file:
        file.write(chapter_name)


def send_email(chapter_name):
    """
    Send an email notification via Resend when a new chapter is detected.
    Make sure your RESEND_API_KEY is set and your 'from' domain is verified in Resend.
    """
    params = {
        # Note: replace this with your own verified sender address from Resend
        "from": "onboarding@resend.dev",
        "to": [RECIPIENT_EMAIL],  # Loaded from .env — no personal info hardcoded
        "subject": "New One Piece Chapter Released!",
        "html": f"<strong>New chapter released:</strong><p>{chapter_name}</p>",
    }
    response = resend.Emails.send(params)
    log(f"Email sent: {response}")


# ── Main logic ──────────────────────────────────────────────────────────────

log("----- Script started -----")

latest = get_latest_chapter()

if latest is None:
    # Something went wrong with the scrape — skip this run and try again later
    log("Could not determine latest chapter this run. Skipping.")
else:
    log(f"Latest chapter on website: {latest}")

    last_seen = load_last_seen()
    log(f"Last saved chapter: {last_seen}")

    if last_seen is None:
        # First time running — just save what's currently there, no email sent
        save_last_seen(latest)
        log("First run: saved the current latest chapter. Will notify on the next new one.")
    elif latest != last_seen:
        # The chapter name changed — a new chapter dropped!
        log("New chapter detected!")
        log(f"Old chapter: {last_seen}")
        log(f"New chapter: {latest}")
        send_email(latest)
        save_last_seen(latest)
    else:
        # Nothing new — all quiet
        log("No new chapter. Checking again later.")
