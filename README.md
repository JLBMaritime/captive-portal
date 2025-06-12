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

## Installation

1. Clone this repository or copy all files to the Raspberry Pi
2. Ensure you have the JLBMaritime logo file (jlb_logo.png) in the static/logo directory
3. Run the installation script as root:

```bash
sudo ./install.sh
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

## Logs

Logs are stored in `/var/log/captive-portal.log` and can be viewed with:

```bash
sudo tail -f /var/log/captive-portal.log
```

## Credits

Developed for JLBMaritime by [Your Name/Company]
