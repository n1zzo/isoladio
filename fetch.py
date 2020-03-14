#!/usr/bin/python3

import os
import argparse
import sys
import sqlite3
from datetime import datetime

database_path = ""
dry_run = False

def connect():
    assert database_path
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS suggestions(id INTEGER NOT NULL PRIMARY KEY, path TEXT, url TEXT, suggester TEXT, played_on INTEGER, suggested_on INTEGER)")
    return (connection, cursor)

def fetch():
    connection, cursor = connect()

    now = int(datetime.now().timestamp())
    results = list(cursor.execute("SELECT id, path FROM suggestions WHERE played_on IS NULL ORDER BY suggested_on ASC LIMIT 1"))

    if len(results) == 0:
        # No unplayed songs, pick a random one
        results = list(cursor.execute("SELECT id, path FROM suggestions ORDER BY random() LIMIT 1"))

    if len(results) == 0:
        return

    assert len(results) == 1
    result = results[0]

    id, path = result
    print(path)

    if not dry_run:
        cursor.execute("UPDATE suggestions SET played_on = ? WHERE id == ?", (now, id))
        connection.commit()

    connection.close()

def main():
    parser = argparse.ArgumentParser(description="Fetch next song to play.")
    parser.add_argument("--dry-run", action="store_true", help="Do not mark the song as played. Use this for testing purposes.")
    parser.add_argument("--db", default="suggestions.db", help="Sqlite database to employ.")
    args = parser.parse_args()

    global dry_run
    dry_run = args.dry_run

    global database_path
    database_path = args.db

    fetch()

    return 0

if __name__ == "__main__":
    sys.exit(main())
