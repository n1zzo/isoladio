#!/usr/bin/env python3

from flask import Flask, render_template, request, redirect
import youtube_dl
import argparse

app = Flask(__name__,
            static_url_path='',
            template_folder="www",
            static_folder="www")


def download_song(url):
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
        ydl.download([url])

@app.route("/")
def root():
    return render_template('index.html')

@app.route('/enqueue', methods=['POST'])
def enqueue():
    download_song(request.form['youtubedl'])
    return redirect("/")

def main():
    parser = argparse.ArgumentParser(description="Run the web frontend.")
    parser.add_argument("--host", default="localhost", help="Host to listen to.")
    parser.add_argument("--port", default=5000, type=int, help="Port to listen to.")
    args = parser.parse_args()

    app.run(host=args.host, port=args.port)

if __name__ == "__main__":
    main()
