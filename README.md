# Setting up the web interface

```
apt install python3-pip ffmpeg espeak-ng
pip3 install --user youtube_dl
pip3 install --user flask
pip3 install --user ffmpeg-python
./frontend.py --host 127.0.0.1 --port 8001 --db suggestions.db
```

# How to install

```
apt install icecast2 ices2
# Choose a password for icecast2, say `goofy`
systemctl start icecast2
# Check if icecast is reachable at http://myserver:8000/

git clone https://github.com/n1zzo/isoladio
cd isoladio
```

Now edit `ices2-config.xml`:

* Set the icecast password (`ices/stream/instance/password`)
* Choose mount name (`ices/stream/instance/mount`). By default, tour stream will
  be available at `http://myserver:8000/mymount.ogg`.

You can now run `ices2`:

```
ices2 ices2-config.xml
```

You stream should now be available.

# nginx configuration

```
location /isoladio/ {
  proxy_pass http://127.0.0.1:8001/;
  proxy_set_header Host $host;
  proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
  proxy_set_header X-Scheme $scheme;
  proxy_set_header X-Script-Name /isoladio;
  proxy_set_header X-Forwarded-Prefix /isoladio;
}

location /icecast/ {
  proxy_pass http://127.0.0.1:8000/;
  proxy_set_header Host $host;
  proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
  proxy_set_header X-Scheme $scheme;
  proxy_set_header X-Script-Name /icecast;
}
```
