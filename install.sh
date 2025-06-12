#!/bin/bash
# JLBMaritime Captive Portal Installation Script

# Exit on any error
set -e

# Function to display messages
print_message() {
    echo -e "\e[1;34m>>> $1\e[0m"
}

# Function to check if running as root
check_root() {
    if [ "$(id -u)" -ne 0 ]; then
        echo "This script must be run as root" 
        exit 1
    fi
}

# Function to install required packages
install_packages() {
    print_message "Updating package lists..."
    apt-get update

    print_message "Installing required packages..."
    apt-get install -y python3 python3-pip network-manager dnsmasq hostapd iptables-persistent
    
    print_message "Installing required Python packages..."
    apt-get install -y python3-flask
}

# Function to create directory structure
create_directories() {
    print_message "Creating directory structure..."
    
    # Create main directory
    mkdir -p /opt/captive-portal
    mkdir -p /opt/captive-portal/static/css
    mkdir -p /opt/captive-portal/static/js
    mkdir -p /opt/captive-portal/static/logo
    mkdir -p /opt/captive-portal/templates
    
    # Create log directory if it doesn't exist
    mkdir -p /var/log
    
    # Set permissions
    chown -R JLBMaritime:JLBMaritime /opt/captive-portal
}

# Function to copy files
copy_files() {
    print_message "Copying files to installation directory..."
    
    # Get the directory of this script
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    
    # Copy Python files
    cp "$SCRIPT_DIR/app.py" /opt/captive-portal/
    cp "$SCRIPT_DIR/network_manager.py" /opt/captive-portal/
    cp "$SCRIPT_DIR/access_point.py" /opt/captive-portal/
    cp "$SCRIPT_DIR/connection_monitor.py" /opt/captive-portal/
    
    # Copy static files
    cp "$SCRIPT_DIR/static/css/style.css" /opt/captive-portal/static/css/
    cp "$SCRIPT_DIR/static/js/main.js" /opt/captive-portal/static/js/
    
    # Copy logo if it exists
    if [ -f "$SCRIPT_DIR/static/logo/jlb_logo.png" ]; then
        cp "$SCRIPT_DIR/static/logo/jlb_logo.png" /opt/captive-portal/static/logo/
    else
        print_message "WARNING: Logo file not found. Please copy jlb_logo.png to /opt/captive-portal/static/logo/"
    fi
    
    # Copy templates
    cp "$SCRIPT_DIR/templates/index.html" /opt/captive-portal/templates/
    cp "$SCRIPT_DIR/templates/success.html" /opt/captive-portal/templates/
    
    # Make scripts executable
    chmod +x /opt/captive-portal/app.py
    chmod +x /opt/captive-portal/connection_monitor.py
    
    # Set ownership
    chown -R JLBMaritime:JLBMaritime /opt/captive-portal
}

# Function to set up systemd services
setup_services() {
    print_message "Setting up systemd services..."
    
    # Create captive portal service
    cat > /etc/systemd/system/captive-portal.service << EOF
[Unit]
Description=JLBMaritime Captive Portal
After=network.target

[Service]
User=JLBMaritime
WorkingDirectory=/opt/captive-portal
ExecStart=/usr/bin/python3 /opt/captive-portal/app.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

    # Create connection monitor service
    cat > /etc/systemd/system/connection-monitor.service << EOF
[Unit]
Description=JLBMaritime Connection Monitor
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /opt/captive-portal/connection_monitor.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    # Reload systemd
    systemctl daemon-reload
    
    # Enable and start services
    systemctl enable captive-portal.service
    systemctl enable connection-monitor.service
}

# Function to configure NetworkManager
configure_network_manager() {
    print_message "Configuring NetworkManager..."
    
    # Create AP configuration
    cat > /etc/NetworkManager/system-connections/JLBMaritime.nmconnection << EOF
[connection]
id=JLBMaritime
uuid=$(uuidgen)
type=wifi
interface-name=wlan0
permissions=
autoconnect=true

[wifi]
mode=ap
ssid=JLBMaritime

[wifi-security]
key-mgmt=wpa-psk
psk=Admin

[ipv4]
method=shared
address1=10.42.0.1/24

[ipv6]
method=ignore
EOF

    # Set proper permissions
    chmod 600 /etc/NetworkManager/system-connections/JLBMaritime.nmconnection
    
    # Restart NetworkManager
    systemctl restart NetworkManager
}

# Main installation function
main() {
    print_message "Starting JLBMaritime Captive Portal installation..."
    
    # Check if running as root
    check_root
    
    # Install required packages
    install_packages
    
    # Create directories
    create_directories
    
    # Copy files
    copy_files
    
    # Set up systemd services
    setup_services
    
    # Configure NetworkManager
    configure_network_manager
    
    print_message "Installation completed successfully!"
    print_message "The captive portal will start automatically on next boot."
    print_message "To start it now, run: systemctl start captive-portal.service"
    print_message "To start the connection monitor now, run: systemctl start connection-monitor.service"
}

# Run main function
main
