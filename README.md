# malioglasi
Crawler for mobilnisvet.com/mobilni-malioglasi


#### Configuration file
# Note: You have to change parameters inside the configuration file before running
```bash
cp malioglasi.conf /etc/malioglasi.conf
```

#### Cron
```bash
echo '*/5 * * * *  root  /usr/local/bin/malioglasi.py' > /etc/cron.d/malioglasi
```

#### Systemd/Timers
##### Copy service and timer to systemd dir
```bash
cp malioglasi.timer malioglasi.service /lib64/systemd/system/
```

##### Enable and start systemd timer
```bash
systemctl enable malioglasi.timer
systemctl start malioglasi.timer
```
