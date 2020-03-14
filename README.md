# Setting up the web interface

```
apt install python3-pip python3-flask
pip3 install --user youtube_dl
./frontend.py --host 127.0.0.1 --port 5000
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
