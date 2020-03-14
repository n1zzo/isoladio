#!/usr/bin/env python3

from datetime import datetime
from fetch import connect
from flask import Flask, render_template, request, redirect, url_for
from os.path import abspath, splitext
from werkzeug.middleware.proxy_fix import ProxyFix
import argparse
import fetch
import youtube_dl

app = Flask(__name__,
            static_url_path='',
            template_folder="www",
            static_folder="www")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_prefix=1)

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
        filename = ydl.prepare_filename(info)
        filename = splitext(filename)[0]+".ogg"
        ydl.download([url])
    return filename

@app.route("/")
def root():
    queue = ["Rick Astley - Never Gonna Give You Up",
                  "Dua Lipa - New Rules"]
    return render_template('index.html', queue=queue)

@app.route('/enqueue', methods=['POST'])
def enqueue():
    url = request.form['youtubedl']
    path = download_song(url)
    connection, cursor = fetch.connect()
    suggestion = [
        abspath(path),
        url,
        "anonymous",
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
    args = parser.parse_args()

    fetch.database_path = args.db

    app.run(host=args.host, port=args.port)

if __name__ == "__main__":
    main()
