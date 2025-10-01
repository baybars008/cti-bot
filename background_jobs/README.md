cp -r ctibot.service /etc/systemd/system/ctibot.service
chmod +x /etc/systemd/system/ctibot.service
systemctl daemon-reload
systemctl enable --now tor
systemctl enable --now ctibot