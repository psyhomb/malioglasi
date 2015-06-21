# malioglasi
Crawler for mobilnisvet.com/mobilni-malioglasi


#### Cron
echo '*/5 * * * *  root  /usr/local/bin/malioglasi.py' > /etc/cron.d/malioglasi


#### Systemd/Timers
### Copy service and timer to systemd dir
cp malioglasi.timer malioglasi.service /lib64/systemd/system/

### Enable and start systemd timer
systemctl enable malioglasi.timer
systemctl start malioglasi.timer
