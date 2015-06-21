# malioglasi
Crawler for mobilnisvet.com/mobilni-malioglasi


# Cron
*/5 * * * * /usr/local/bin/malioglasi.py


# Systemd/Timers
# Copy service and timer to systemd dir
cp malioglasi.timer malioglasi.service /lib64/systemd/system/

# Enable and start systemd timer
systemctl enable malioglasi.timer
systemctl start malioglasi.timer
