import os
import json
import sqlite3
import platform
from pathlib import Path

def find_all_chromium_bookmark_files():
    """Find every Bookmarks file in every Chromium browser profile."""
    if platform.system() != "Windows":
        return []

    base = Path(os.environ["LOCALAPPDATA"])
    browser_dirs = {
        "chrome": "Google/Chrome/User Data",
        "brave": "BraveSoftware/Brave-Browser/User Data",
        "edge": "Microsoft/Edge/User Data",
        "opera": "Opera Software/Opera Stable"  # Opera stores Bookmarks differently
    }

    bookmark_files = []

    for browser_name, browser_path in browser_dirs.items():
        browser_dir = base / browser_path

        if not browser_dir.exists():
            continue

        # Chromium browsers have multiple profile folders:
        # "Default", "Profile 1", "Profile 2", etc.
        for profile in browser_dir.iterdir():
            if profile.is_dir():
                bookmarks = profile / "Bookmarks"
                if bookmarks.exists():
                    bookmark_files.append((browser_name, profile.name, bookmarks))

    return bookmark_files


def read_chromium_bookmarks(browser, profile, path):
    """Read bookmarks from a Chrome/Brave/Edge/Opera Bookmarks JSON."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return []

    results = []

    def walk(node):
        if isinstance(node, dict):
            if node.get("type") == "url":
                results.append({
                    "browser": browser,
                    "profile": profile,
                    "name": node.get("name", "(no title)"),
                    "url": node.get("url")
                })
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(data)
    return results


def find_all_firefox_dbs():
    """Find all Firefox profile databases."""
    if platform.system() != "Windows":
        return []

    base = Path(os.environ["APPDATA"]) / "Mozilla/Firefox/Profiles"
    if not base.exists():
        return []

    dbs = []
    for folder in base.iterdir():
        if folder.is_dir() and (folder / "places.sqlite").exists():
            dbs.append((folder.name, folder / "places.sqlite"))
    return dbs


def read_firefox_bookmarks(profile, db_path):
    """Read Firefox bookmarks from places.sqlite."""
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
    except Exception:
        return []

    query = """
    SELECT moz_bookmarks.title, moz_places.url
    FROM moz_bookmarks
    JOIN moz_places ON moz_bookmarks.fk = moz_places.id
    WHERE moz_places.url IS NOT NULL;
    """

    results = []
    for title, url in cur.execute(query):
        results.append({
            "browser": "firefox",
            "profile": profile,
            "name": title if title else "(no title)",
            "url": url
        })

    conn.close()
    return results


def main():
    all_bookmarks = []

    # Chromium browsers (ALL PROFILES)
    for browser, profile, path in find_all_chromium_bookmark_files():
        all_bookmarks.extend(read_chromium_bookmarks(browser, profile, path))

    # Firefox (ALL PROFILES)
    for profile, db in find_all_firefox_dbs():
        all_bookmarks.extend(read_firefox_bookmarks(profile, db))

    if not all_bookmarks:
        print("No bookmarks found.")
        return

    print("\n=== BOOKMARKS (ALL BROWSERS, ALL PROFILES) ===\n")
    for b in all_bookmarks:
        print(f"[{b['browser']} - {b['profile']}] {b['name']} -> {b['url']}")

    print(f"\nTOTAL: {len(all_bookmarks)} bookmarks found across all profiles.")


if __name__ == "__main__":
    main()
