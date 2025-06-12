#!/usr/bin/env python3
# network_manager.py - Interface to NetworkManager for the JLBMaritime Captive Portal

import subprocess
import json
import re
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("/var/log/captive-portal.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("network_manager")

class NetworkManager:
    """
    Interface to NetworkManager for scanning networks and managing connections
    """
    
    @staticmethod
    def scan_networks():
        """
        Scan for available Wi-Fi networks
        
        Returns:
            list: List of dictionaries containing network information
        """
        try:
            logger.info("Scanning for Wi-Fi networks...")
            # Run nmcli to scan for networks
            cmd = ["nmcli", "-t", "-f", "SSID,SIGNAL,SECURITY", "device", "wifi", "list", "--rescan", "yes"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            networks = []
            for line in result.stdout.splitlines():
                if not line.strip():
                    continue
                    
                # Parse the output
                parts = line.split(':')
                if len(parts) >= 3:
                    ssid = parts[0]
                    
                    # Skip empty SSIDs or the JLBMaritime AP itself
                    if not ssid or ssid == "JLBMaritime":
                        continue
                        
                    try:
                        signal = int(parts[1])
                    except ValueError:
                        signal = 0
                        
                    # Parse security
                    security_str = ':'.join(parts[2:])
                    security = []
                    
                    if "WPA2" in security_str:
                        security.append("WPA2")
                    if "WPA1" in security_str:
                        security.append("WPA")
                    if "WEP" in security_str:
                        security.append("WEP")
                    
                    networks.append({
                        "ssid": ssid,
                        "signal": signal,
                        "security": security
                    })
            
            # Remove duplicates (by SSID)
            unique_networks = []
            seen_ssids = set()
            
            for network in networks:
                if network["ssid"] not in seen_ssids:
                    seen_ssids.add(network["ssid"])
                    unique_networks.append(network)
            
            logger.info(f"Found {len(unique_networks)} unique networks")
            return unique_networks
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error scanning networks: {e}")
            logger.error(f"Error output: {e.stderr}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error scanning networks: {e}")
            return []
    
    @staticmethod
    def connect_to_network(ssid, password=None):
        """
        Connect to a Wi-Fi network
        
        Args:
            ssid (str): The network SSID
            password (str, optional): The network password
            
        Returns:
            bool: True if connection was successful, False otherwise
            str: Status message
        """
        try:
            logger.info(f"Attempting to connect to network: {ssid}")
            
            # Check if connection already exists
            cmd = ["nmcli", "-t", "-f", "NAME", "connection", "show"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            connection_exists = False
            for line in result.stdout.splitlines():
                if line.strip() == ssid:
                    connection_exists = True
                    break
            
            if connection_exists:
                # Modify existing connection
                logger.info(f"Connection for {ssid} already exists, updating...")
                if password:
                    # Update the password for the existing connection
                    cmd = ["nmcli", "connection", "modify", ssid, "wifi-sec.psk", password]
                    subprocess.run(cmd, check=True)
                
                # Activate the connection
                cmd = ["nmcli", "connection", "up", ssid]
                subprocess.run(cmd, check=True)
            else:
                # Create a new connection
                logger.info(f"Creating new connection for {ssid}")
                if password:
                    cmd = ["nmcli", "device", "wifi", "connect", ssid, "password", password]
                else:
                    cmd = ["nmcli", "device", "wifi", "connect", ssid]
                
                subprocess.run(cmd, check=True)
            
            # Verify connection
            time.sleep(5)  # Give some time for connection to establish
            
            # Check if we're connected to the expected network
            cmd = ["nmcli", "-t", "-f", "NAME,DEVICE,STATE", "connection", "show", "--active"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            for line in result.stdout.splitlines():
                parts = line.split(':')
                if len(parts) >= 3 and parts[0] == ssid and parts[2] == "activated":
                    logger.info(f"Successfully connected to {ssid}")
                    
                    # Get IP address
                    cmd = ["nmcli", "-t", "-f", "IP4.ADDRESS", "connection", "show", ssid]
                    ip_result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                    
                    ip_address = "Unknown"
                    for ip_line in ip_result.stdout.splitlines():
                        if ip_line.startswith("IP4.ADDRESS"):
                            ip_match = re.search(r'\d+\.\d+\.\d+\.\d+', ip_line)
                            if ip_match:
                                ip_address = ip_match.group(0)
                    
                    # Get signal strength
                    cmd = ["nmcli", "-t", "-f", "SIGNAL", "device", "wifi", "list", "ifname", parts[1], "ssid", ssid]
                    signal_result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                    
                    signal_strength = 0
                    for signal_line in signal_result.stdout.splitlines():
                        try:
                            signal_strength = int(signal_line.strip())
                            break
                        except ValueError:
                            pass
                    
                    return True, {
                        "message": f"Successfully connected to {ssid}",
                        "ip_address": ip_address,
                        "signal_strength": signal_strength
                    }
            
            logger.error(f"Failed to verify connection to {ssid}")
            return False, {"message": f"Failed to connect to {ssid}. Please try again."}
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error connecting to network: {e}")
            logger.error(f"Error output: {e.stderr}")
            
            error_message = "Failed to connect to network"
            if "Secrets were required" in e.stderr:
                error_message = "Invalid password. Please try again."
            
            return False, {"message": error_message}
        except Exception as e:
            logger.error(f"Unexpected error connecting to network: {e}")
            return False, {"message": f"Unexpected error: {str(e)}"}
    
    @staticmethod
    def get_active_connection():
        """
        Get information about the currently active Wi-Fi connection
        
        Returns:
            dict: Connection information or None if not connected
        """
        try:
            # Get active connections
            cmd = ["nmcli", "-t", "-f", "NAME,TYPE,DEVICE,STATE", "connection", "show", "--active"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            for line in result.stdout.splitlines():
                parts = line.split(':')
                if len(parts) >= 4 and parts[1] == "802-11-wireless" and parts[3] == "activated":
                    ssid = parts[0]
                    device = parts[2]
                    
                    # Get IP address
                    cmd = ["nmcli", "-t", "-f", "IP4.ADDRESS", "connection", "show", ssid]
                    ip_result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                    
                    ip_address = "Unknown"
                    for ip_line in ip_result.stdout.splitlines():
                        if ip_line.startswith("IP4.ADDRESS"):
                            ip_match = re.search(r'\d+\.\d+\.\d+\.\d+', ip_line)
                            if ip_match:
                                ip_address = ip_match.group(0)
                    
                    # Get signal strength
                    cmd = ["nmcli", "-t", "-f", "SIGNAL", "device", "wifi", "list", "ifname", device, "ssid", ssid]
                    signal_result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                    
                    signal_strength = 0
                    for signal_line in signal_result.stdout.splitlines():
                        try:
                            signal_strength = int(signal_line.strip())
                            break
                        except ValueError:
                            pass
                    
                    return {
                        "ssid": ssid,
                        "ip_address": ip_address,
                        "signal_strength": signal_strength,
                        "device": device
                    }
            
            return None
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error getting active connection: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting active connection: {e}")
            return None
    
    @staticmethod
    def setup_ap_mode():
        """
        Set up the device as an access point
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info("Setting up Access Point mode")
            
            # Check if JLBMaritime connection already exists
            cmd = ["nmcli", "-t", "-f", "NAME", "connection", "show"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            ap_exists = False
            for line in result.stdout.splitlines():
                if line.strip() == "JLBMaritime":
                    ap_exists = True
                    break
            
            if ap_exists:
                logger.info("JLBMaritime AP connection already exists, activating it")
                cmd = ["nmcli", "connection", "up", "JLBMaritime"]
                subprocess.run(cmd, check=True)
            else:
                logger.info("Creating JLBMaritime AP connection")
                
                # Create a new AP connection
                cmd = [
                    "nmcli", "connection", "add",
                    "type", "wifi",
                    "ifname", "*",
                    "con-name", "JLBMaritime",
                    "autoconnect", "yes",
                    "ssid", "JLBMaritime",
                    "mode", "ap",
                    "ipv4.method", "shared",
                    "ipv4.addresses", "10.42.0.1/24",
                    "wifi-sec.key-mgmt", "wpa-psk",
                    "wifi-sec.psk", "Admin"
                ]
                subprocess.run(cmd, check=True)
                
                # Activate the connection
                cmd = ["nmcli", "connection", "up", "JLBMaritime"]
                subprocess.run(cmd, check=True)
            
            logger.info("Access Point mode setup completed")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error setting up AP mode: {e}")
            logger.error(f"Error output: {e.stderr}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error setting up AP mode: {e}")
            return False
    
    @staticmethod
    def check_connection_status():
        """
        Check if there's an active Wi-Fi connection to a network (not AP mode)
        
        Returns:
            bool: True if connected to a Wi-Fi network, False otherwise
        """
        try:
            # Get active connections
            cmd = ["nmcli", "-t", "-f", "NAME,TYPE,DEVICE,STATE", "connection", "show", "--active"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            for line in result.stdout.splitlines():
                parts = line.split(':')
                if len(parts) >= 4 and parts[1] == "802-11-wireless" and parts[3] == "activated":
                    # If we're connected to something other than our AP
                    if parts[0] != "JLBMaritime":
                        return True
            
            return False
            
        except subprocess.CalledProcessError:
            return False
        except Exception as e:
            logger.error(f"Unexpected error checking connection status: {e}")
            return False

# For testing
if __name__ == "__main__":
    networks = NetworkManager.scan_networks()
    print(json.dumps(networks, indent=2))
    
    active = NetworkManager.get_active_connection()
    if active:
        print(f"Connected to: {active['ssid']}")
        print(f"IP Address: {active['ip_address']}")
        print(f"Signal Strength: {active['signal_strength']}%")
    else:
        print("Not connected to any network")
