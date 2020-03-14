#!/usr/bin/env python3

from flask import Flask, render_template, request, redirect
import youtube_dl

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
def main():
    return render_template('index.html')

@app.route('/enqueue', methods=['POST'])
def enqueue():
    download_song(request.form['youtubedl'])
    return redirect("/")
#    return render_template('index.html')
 
if __name__ == "__main__":
    app.run()
