#!/usr/bin/env python3
# access_point.py - Access Point setup and DNS redirection for JLBMaritime Captive Portal

import subprocess
import os
import logging
import shutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("/var/log/captive-portal.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("access_point")

class AccessPoint:
    """
    Handles setting up the access point and DNS redirection for captive portal
    """
    
    @staticmethod
    def setup_dnsmasq():
        """
        Set up dnsmasq configuration for DNS redirection
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info("Setting up dnsmasq configuration")
            
            # Backup the original config if it exists and we haven't already
            if os.path.exists("/etc/dnsmasq.conf") and not os.path.exists("/etc/dnsmasq.conf.original"):
                logger.info("Backing up original dnsmasq configuration")
                shutil.copy2("/etc/dnsmasq.conf", "/etc/dnsmasq.conf.original")
            
            # Create a new dnsmasq configuration
            dnsmasq_config = """# JLBMaritime Captive Portal dnsmasq configuration
interface=wlan0
dhcp-range=10.42.0.2,10.42.0.20,255.255.255.0,24h
dhcp-option=3,10.42.0.1
dhcp-option=6,10.42.0.1
address=/#/10.42.0.1
"""
            
            with open("/etc/dnsmasq.conf", "w") as f:
                f.write(dnsmasq_config)
                
            logger.info("dnsmasq configuration created")
            
            # Restart dnsmasq service
            subprocess.run(["systemctl", "restart", "dnsmasq"], check=True)
            logger.info("dnsmasq service restarted")
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error restarting dnsmasq: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error setting up dnsmasq: {e}")
            return False
    
    @staticmethod
    def restore_dnsmasq():
        """
        Restore the original dnsmasq configuration
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info("Restoring original dnsmasq configuration")
            
            if os.path.exists("/etc/dnsmasq.conf.original"):
                shutil.copy2("/etc/dnsmasq.conf.original", "/etc/dnsmasq.conf")
                logger.info("Original dnsmasq configuration restored")
            else:
                logger.warning("Original dnsmasq configuration not found, cannot restore")
                return False
                
            # Restart dnsmasq service
            subprocess.run(["systemctl", "restart", "dnsmasq"], check=True)
            logger.info("dnsmasq service restarted")
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error restarting dnsmasq: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error restoring dnsmasq: {e}")
            return False
    
    @staticmethod
    def setup_hostapd():
        """
        Set up hostapd configuration for the access point (if needed)
        
        Note: NetworkManager should handle this, but we include this method
        in case manual configuration is needed.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info("Setting up hostapd configuration")
            
            # Create hostapd configuration
            hostapd_config = """# JLBMaritime Captive Portal hostapd configuration
interface=wlan0
driver=nl80211
ssid=JLBMaritime
hw_mode=g
channel=7
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=Admin
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
"""
            
            with open("/etc/hostapd/hostapd.conf", "w") as f:
                f.write(hostapd_config)
                
            # Update hostapd default configuration
            with open("/etc/default/hostapd", "w") as f:
                f.write('DAEMON_CONF="/etc/hostapd/hostapd.conf"')
                
            logger.info("hostapd configuration created")
            
            # Enable and restart hostapd service
            subprocess.run(["systemctl", "enable", "hostapd"], check=True)
            subprocess.run(["systemctl", "restart", "hostapd"], check=True)
            logger.info("hostapd service enabled and restarted")
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error configuring hostapd: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error setting up hostapd: {e}")
            return False
    
    @staticmethod
    def enable_ip_forwarding():
        """
        Enable IP forwarding
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info("Enabling IP forwarding")
            
            # Enable IP forwarding
            with open("/proc/sys/net/ipv4/ip_forward", "w") as f:
                f.write("1")
                
            # Add to sysctl.conf to make permanent
            with open("/etc/sysctl.conf", "a") as f:
                f.write("\n# JLBMaritime Captive Portal\nnet.ipv4.ip_forward=1\n")
                
            # Apply changes
            subprocess.run(["sysctl", "-p"], check=True)
            
            logger.info("IP forwarding enabled")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error enabling IP forwarding: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error enabling IP forwarding: {e}")
            return False
    
    @staticmethod
    def setup_iptables():
        """
        Set up iptables for captive portal redirection
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info("Setting up iptables rules")
            
            # Clear existing rules
            subprocess.run(["iptables", "-F"], check=True)
            subprocess.run(["iptables", "-t", "nat", "-F"], check=True)
            
            # Allow established connections
            subprocess.run(["iptables", "-A", "INPUT", "-m", "conntrack", "--ctstate", "ESTABLISHED,RELATED", "-j", "ACCEPT"], check=True)
            
            # Allow local connections
            subprocess.run(["iptables", "-A", "INPUT", "-i", "lo", "-j", "ACCEPT"], check=True)
            
            # Allow SSH (for admin access)
            subprocess.run(["iptables", "-A", "INPUT", "-p", "tcp", "--dport", "22", "-j", "ACCEPT"], check=True)
            
            # Allow DNS
            subprocess.run(["iptables", "-A", "INPUT", "-i", "wlan0", "-p", "udp", "--dport", "53", "-j", "ACCEPT"], check=True)
            subprocess.run(["iptables", "-A", "INPUT", "-i", "wlan0", "-p", "tcp", "--dport", "53", "-j", "ACCEPT"], check=True)
            
            # Allow DHCP
            subprocess.run(["iptables", "-A", "INPUT", "-i", "wlan0", "-p", "udp", "--dport", "67", "-j", "ACCEPT"], check=True)
            
            # Allow HTTP/HTTPS (for captive portal)
            subprocess.run(["iptables", "-A", "INPUT", "-i", "wlan0", "-p", "tcp", "--dport", "80", "-j", "ACCEPT"], check=True)
            subprocess.run(["iptables", "-A", "INPUT", "-i", "wlan0", "-p", "tcp", "--dport", "443", "-j", "ACCEPT"], check=True)
            
            # Redirect HTTP traffic to captive portal
            subprocess.run([
                "iptables", "-t", "nat", "-A", "PREROUTING", 
                "-i", "wlan0", "-p", "tcp", "--dport", "80", 
                "-j", "DNAT", "--to-destination", "10.42.0.1:5000"
            ], check=True)
            
            # Redirect HTTPS traffic to captive portal
            # This won't work perfectly due to SSL, but helps with captive portal detection
            subprocess.run([
                "iptables", "-t", "nat", "-A", "PREROUTING", 
                "-i", "wlan0", "-p", "tcp", "--dport", "443", 
                "-j", "DNAT", "--to-destination", "10.42.0.1:5000"
            ], check=True)
            
            # Save iptables rules
            iptables_save_cmd = "iptables-save > /etc/iptables/rules.v4"
            subprocess.run(iptables_save_cmd, shell=True, check=True)
            
            logger.info("iptables rules configured and saved")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error setting up iptables: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error setting up iptables: {e}")
            return False
    
    @staticmethod
    def configure_systemd_services():
        """
        Configure systemd services for the captive portal
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info("Configuring systemd services")
            
            # Create service for captive portal
            captive_portal_service = """[Unit]
Description=JLBMaritime Captive Portal
After=network.target

[Service]
User=JLBMaritime
WorkingDirectory=/opt/captive-portal
ExecStart=/usr/bin/python3 app.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
"""
            
            with open("/etc/systemd/system/captive-portal.service", "w") as f:
                f.write(captive_portal_service)
                
            # Create service for connection monitor
            connection_monitor_service = """[Unit]
Description=JLBMaritime Connection Monitor
After=network.target

[Service]
Type=simple
ExecStart=/opt/captive-portal/connection_monitor.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
            
            with open("/etc/systemd/system/connection-monitor.service", "w") as f:
                f.write(connection_monitor_service)
                
            # Reload systemd
            subprocess.run(["systemctl", "daemon-reload"], check=True)
            
            # Enable services
            subprocess.run(["systemctl", "enable", "captive-portal.service"], check=True)
            subprocess.run(["systemctl", "enable", "connection-monitor.service"], check=True)
            
            logger.info("Systemd services configured and enabled")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error configuring systemd services: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error configuring systemd services: {e}")
            return False
    
    @staticmethod
    def setup():
        """
        Perform complete access point setup
        
        Returns:
            bool: True if successful, False otherwise
        """
        success = True
        
        # Setup dnsmasq
        if not AccessPoint.setup_dnsmasq():
            logger.error("Failed to set up dnsmasq")
            success = False
        
        # Enable IP forwarding
        if not AccessPoint.enable_ip_forwarding():
            logger.error("Failed to enable IP forwarding")
            success = False
        
        # Setup iptables
        if not AccessPoint.setup_iptables():
            logger.error("Failed to set up iptables")
            success = False
        
        # Configure systemd services
        if not AccessPoint.configure_systemd_services():
            logger.error("Failed to configure systemd services")
            success = False
        
        if success:
            logger.info("Access point setup completed successfully")
        else:
            logger.warning("Access point setup completed with errors")
        
        return success

# For testing
if __name__ == "__main__":
    AccessPoint.setup()
