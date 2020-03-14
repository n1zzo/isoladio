#!/usr/bin/env python3

from datetime import datetime
from fetch import connect
from flask import Flask, render_template, request, redirect, url_for
from os.path import abspath, splitext
from werkzeug.middleware.proxy_fix import ProxyFix
import re
import argparse
import fetch
import youtube_dl

import shutil
import os
import ffmpeg
import tempfile
from shutil import which
import subprocess

from urllib.parse import urlparse

max_duration = 0
safe_categories = set()

espeak = which("espeak-ng") or which("espeak")
assert espeak

app = Flask(__name__,
            static_url_path='',
            template_folder="www",
            static_folder="www")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_prefix=1)

def say_over(message, base_path):
    output = tempfile.NamedTemporaryFile(suffix=".ogg", delete=False)
    with tempfile.NamedTemporaryFile() as temporary:
        subprocess.check_call([espeak, "-v", "it", "-w", temporary.name, message])
        speech = ffmpeg.input(temporary.name).filter('volume', 10)
        base = ffmpeg.input(base_path)
        merged_audio = ffmpeg.filter([base, speech], 'amix')
        ffmpeg.overwrite_output(merged_audio.output(output.name)).run()
    return output.name

def download_song(url):
    filename = ""
    ydl_opts = {
        'extractaudio': True,
        'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'vorbis',
                'preferredquality': '0',
                'nopostoverwrites': False,
        }],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

        # Prevent too long submissions
        if info["duration"] > max_duration:
            return None

        # If safe-categories are active, enforce them
        if (safe_categories
            and not (set(map(str.lower, info["categories"])) & safe_categories)):
            return None

        filename = ydl.prepare_filename(info)
        filename = splitext(filename)[0]+".ogg"
        ydl.download([url])

    with_speech = say_over("Questo pezzo vi è offerto da Asdinare", filename)
    os.unlink(filename)
    shutil.move(with_speech, filename)

    return filename

@app.route("/")
def root():
    connection, cursor = connect()
    now = int(datetime.now().timestamp())
    results = list(cursor.execute("SELECT path FROM suggestions WHERE played_on IS NULL ORDER BY suggested_on ASC"))
    name_pattern = r'.*/(.*)-[^-]*$'
    queue = map(lambda x: re.search(name_pattern, x[0]).group(1), results)
    return render_template('index.html', queue=queue)

@app.route('/enqueue', methods=['POST'])
def enqueue():
    url = request.form['youtubedl']
    submitter = request.form['submitter']
    submitter = "anonymous" if submitter == "" else submitter
    if url == "" or urlparse(url).netloc not in ["youtube.com", "www.youtube.com"]:
        return redirect(url_for("root"))

    path = download_song(url)

    if not path:
        return redirect(url_for("root"))

    connection, cursor = fetch.connect()
    suggestion = [
        abspath(path),
        url,
        submitter,
        int(datetime.now().timestamp())
    ]
    sql = ''' INSERT INTO suggestions(path, url, suggester, suggested_on)
              VALUES(?,?,?,?) '''
    cursor.execute(sql, suggestion)
    connection.commit()
    connection.close()

    return redirect(url_for("root"))

def main():
    parser = argparse.ArgumentParser(description="Run the web frontend.")
    parser.add_argument("--host", default="localhost", help="Host to listen to.")
    parser.add_argument("--port", default=5000, type=int, help="Port to listen to.")
    parser.add_argument("--db", default="suggestions.db", help="Sqlite database to employ.")
    parser.add_argument("--safe-categories", default="", help="Sqlite database to employ.")
    parser.add_argument("--max-duration", default=(60 * 7), help="Maximum duration of the track to enqueue.")
    args = parser.parse_args()

    fetch.database_path = args.db

    global max_duration
    max_duration = args.max_duration

    global safe_categories
    if args.safe_categories:
        safe_categories = set(map(str.lower, args.safe_categories.split(",")))

    app.run(host=args.host, port=args.port)

if __name__ == "__main__":
    main()
