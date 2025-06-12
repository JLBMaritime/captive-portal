# JLBMaritime Captive Portal

A Wi-Fi captive portal solution for JLBMaritime AIS receivers/servers, allowing customers to easily configure Wi-Fi connection details through a web interface.

## Overview

This solution creates a captive portal that allows end users to configure their JLBMaritime AIS receiver/server to connect to their Wi-Fi network. When the device powers on and cannot connect to any known Wi-Fi networks, it creates its own access point named "JLBMaritime" with the password "Admin". Users can connect to this network and will be automatically redirected to a web interface where they can select their Wi-Fi network and enter credentials.

## Features

- Responsive web interface that works on desktop PCs, laptops, iPhones, and Android phones
- Automatic scanning for available Wi-Fi networks
- Secure storage of Wi-Fi credentials using NetworkManager
- Automatic reconnection to configured networks after power loss
- Fallback to captive portal mode if no known networks are available
- Branded with JLBMaritime logo and styling

## System Requirements

- Raspberry Pi 4B 2GB
- Raspberry Pi OS Bookworm (64-bit)
- Python 3.9+
- NetworkManager
- Wi-Fi hardware capability

### Required Packages

The installation script will automatically install the following packages:
- python3
- python3-flask
- network-manager
- dnsmasq
- hostapd
- iptables-persistent

## Installation

### Prerequisites

Before installing the captive portal, you need to set up your Raspberry Pi:

1. Install Raspberry Pi OS Bookworm (64-bit) on your Raspberry Pi 4B 2GB
2. Ensure the username is set to "JLBMaritime" and hostname to "AIS" during OS installation
3. Connect to the internet to install required packages

### Installing Git

First, install Git on your Raspberry Pi:

```bash
# Update package lists
sudo apt update

# Install Git
sudo apt install -y git

# Verify installation
git --version
```

### Installing the Captive Portal

#### Option 1: Using Git (Recommended)

1. Clone the repository:
```bash
# Navigate to a suitable directory
cd ~

# Clone the repository (replace with your actual repository URL)
git clone https://github.com/JLBMaritime/captive-portal.git

# Navigate to the project directory
cd captive-portal
```

2. Ensure you have the JLBMaritime logo file (jlb_logo.png) in the static/logo directory

3. Run the installation script as root:
```bash
sudo ./install.sh
```

4. Reboot the Raspberry Pi:
```bash
sudo reboot
```

#### Option 2: Manual Installation

If you received the files via other means (USB drive, etc.):

1. Copy all files to a directory on the Raspberry Pi
2. Ensure you have the JLBMaritime logo file (jlb_logo.png) in the static/logo directory
3. Make the installation script executable:
```bash
chmod +x install.sh
```
4. Run the installation script as root:
```bash
sudo ./install.sh
```
5. Reboot the Raspberry Pi:
```bash
sudo reboot
```

The installation script will:
- Install all required dependencies
- Configure the necessary services
- Set up the Wi-Fi access point
- Configure the captive portal
- Set up automatic startup on boot

## Directory Structure

```
/
├── app.py                # Main Flask application
├── network_manager.py    # NetworkManager interface
├── access_point.py       # AP setup and DNS redirection
├── connection_monitor.py # Connection monitoring service
├── install.sh            # Installation script
├── static/
│   ├── css/
│   │   └── style.css     # Stylesheet
│   ├── js/
│   │   └── main.js       # Frontend JavaScript
│   └── logo/
│       └── jlb_logo.png  # JLBMaritime logo
└── templates/
    ├── index.html        # Main captive portal page
    └── success.html      # Connection success page
```

## Usage

After installation, reboot the Raspberry Pi or start the services manually:

```bash
sudo systemctl start captive-portal.service
sudo systemctl start connection-monitor.service
```

To connect an AIS receiver/server to a Wi-Fi network:

1. Power on the AIS receiver/server
2. If no known networks are available, it will create a "JLBMaritime" access point
3. Connect to the "JLBMaritime" Wi-Fi network (password: "Admin")
4. A captive portal should automatically open; if not, navigate to http://10.42.0.1:5000
5. Select your Wi-Fi network from the list and enter the password
6. Click "Connect" and wait for the connection to be established
7. Once connected, the AIS receiver/server will switch to client mode and connect to your network

## Troubleshooting

- **Cannot connect to the "JLBMaritime" access point**: Ensure the AIS receiver/server is powered on and not already connected to another network.
- **Captive portal doesn't automatically open**: Try navigating to http://10.42.0.1:5000 in your browser.
- **Connection fails**: Verify the Wi-Fi password is correct. Try moving closer to your Wi-Fi router to improve signal strength.
- **Device doesn't reconnect after power loss**: The device attempts to reconnect to known networks in order of last connection. Ensure your network is available and has a strong signal.

For detailed testing instructions and troubleshooting guidance, please refer to the [TESTING.md](TESTING.md) file.

## Logs

Logs are stored in `/var/log/captive-portal.log` and can be viewed with:

```bash
sudo tail -f /var/log/captive-portal.log
```

## Credits

Developed for JLBMaritime by [Your Name/Company]
