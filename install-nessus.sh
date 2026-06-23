#!/bin/bash

# install-nessus.sh - Automated installation of Nessus on Ubuntu/Debian

set -e

# Step 1: Update system
echo "[+] Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Step 2: Download Nessus
echo "[+] Downloading Nessus installer..."
wget -O Nessus.deb "https://www.tenable.com/downloads/api/v1/public/pages/nessus/downloads/nessus-10.6.1-debian10_amd64.deb"

# Step 3: Install Nessus
echo "[+] Installing Nessus package..."
sudo dpkg -i Nessus.deb || sudo apt --fix-broken install -y

# Step 4: Enable and start the service
echo "[+] Enabling and starting Nessus service..."
sudo systemctl enable nessusd.service
sudo systemctl start nessusd.service

# Final Output
echo "[✔] Installation complete!"
echo "[+] Visit: https://localhost:8834 or https://<your-server-ip>:8834 to finish setup"
echo "[!] You may need to accept a self-signed certificate in your browser."
echo "[!] Register for a free key at https://www.tenable.com/products/nessus/nessus-essentials"
