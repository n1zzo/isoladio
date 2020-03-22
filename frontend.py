#!/usr/bin/env python3

from datetime import datetime
from fetch import connect
from flask import Flask, render_template, request, redirect, url_for, jsonify
from os.path import abspath, splitext
from shutil import which
from urllib.parse import urlparse
from werkzeug.middleware.proxy_fix import ProxyFix
import argparse
import fetch
import ffmpeg
import os
import re
import shutil
import subprocess
import tempfile
import youtube_dl

max_duration = 0
safe_categories = set()

espeak = which("espeak-ng") or which("espeak")
assert espeak

app = Flask(__name__,
            static_url_path='',
            template_folder="www",
            static_folder="www")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_prefix=1)


def is_ascii(value):
    try:
        value.encode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True


def say_over(message, base_path):
    output = tempfile.NamedTemporaryFile(suffix=".ogg", delete=False)
    with tempfile.NamedTemporaryFile() as temporary:
        subprocess.check_call([espeak,
                               "-v", "it", "-w",
                               temporary.name, message])
        speech = ffmpeg.input(temporary.name).filter('volume', 10)
        base = ffmpeg.input(base_path)
        merged_audio = ffmpeg.filter([base, speech], 'amix')
        ffmpeg.overwrite_output(merged_audio.output(output.name)).run()
    return output.name


def download_song(url, submitter):
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
        if (safe_categories and not
                (set(map(str.lower, info["categories"])) & safe_categories)):
            return None

        filename = ydl.prepare_filename(info)
        filename = splitext(filename)[0]+".ogg"
        ydl.download([url])

    with_speech = say_over("Questo pezzo vi è offerto da " + submitter,
                           filename)
    os.unlink(filename)
    shutil.move(with_speech, filename)

    return filename


@app.route("/")
def root():
    connection, cursor = connect()
    results = list(cursor.execute(
        "SELECT path "
        "FROM suggestions "
        "WHERE played_on IS NULL "
        "ORDER BY suggested_on ASC"))
    name_pattern = r'.*/(.*)-[^-]*$'
    queue = map(lambda x: re.search(name_pattern, x[0]).group(1), results)
    return render_template('index.html', queue=queue)


@app.route('/search', methods=['GET'])
def search():
    connection, cursor = fetch.connect()
    query = request.args["query"]
    app.logger.info(query)
    results = list(cursor.execute(
        "SELECT torrents.name, files.infohash, files.index_ "
        "FROM files_fts "
        "JOIN files "
        "     ON files_fts.infohash = files.infohash "
        "     AND files_fts.index_ = files.index_ "
        "JOIN torrents "
        "     ON files.infohash = torrents.infohash "
        "WHERE files_fts MATCH ? "
        "ORDER BY rank; ",
        [query]
    ))
    results = map(lambda x: {"name":x[0], "infohash":x[1], "index":x[2]}, results)
    return jsonify({"status": "success", "data":list(results)})


@app.route('/enqueue', methods=['POST'])
def enqueue():
    url = request.form['youtubedl']

    submitter = request.form['submitter']
    submitter = ("anonymous"
                 if (not submitter
                     or len(submitter) > 15
                     or not is_ascii(submitter)
                     or not submitter.isalnum())
                 else submitter)

    if (not url
        or urlparse(url).netloc not in ["youtube.com",
                                        "www.youtube.com",
                                        "youtu.be"]):
        return redirect(url_for("root"))

    path = download_song(url, submitter)

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
    parser.add_argument("--host", default="localhost",
                        help="Host to listen to.")
    parser.add_argument("--port", default=5000,
                        type=int, help="Port to listen to.")
    parser.add_argument("--db", default="suggestions.db",
                        help="Sqlite database to employ.")
    parser.add_argument("--safe-categories", default="",
                        help="Sqlite database to employ.")
    parser.add_argument("--max-duration", default=(60 * 7),
                        help="Maximum duration of the track to enqueue.")
    args = parser.parse_args()

    fetch.database_path = args.db

    global max_duration
    max_duration = args.max_duration

    global safe_categories
    if args.safe_categories:
        safe_categories = set(map(str.lower, args.safe_categories.split(",")))

    app.run(host=args.host, port=args.port, debug=True)


if __name__ == "__main__":
    main()
