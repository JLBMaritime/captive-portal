#!/usr/bin/env python3
# connection_monitor.py - Monitor connection status and switch between AP and client mode

import time
import logging
import os
import sys
from network_manager import NetworkManager
from access_point import AccessPoint

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("/var/log/captive-portal.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("connection_monitor")

class ConnectionMonitor:
    """
    Monitors connection status and handles switching between AP and client mode
    """
    
    @staticmethod
    def check_internet_connection():
        """
        Check if there is an internet connection
        
        Returns:
            bool: True if internet is available, False otherwise
        """
        try:
            # Ping Google's DNS server
            response = os.system("ping -c 1 -W 2 8.8.8.8 > /dev/null 2>&1")
            return response == 0
        except Exception:
            return False
    
    @staticmethod
    def run():
        """
        Main monitoring loop
        """
        logger.info("Starting connection monitor")
        
        # Wait for system to fully start up
        time.sleep(30)
        
        while True:
            try:
                # Check if we're connected to a Wi-Fi network (not our AP)
                is_connected = NetworkManager.check_connection_status()
                
                if is_connected:
                    logger.info("Connected to a Wi-Fi network")
                    
                    # Check internet connectivity
                    if ConnectionMonitor.check_internet_connection():
                        logger.info("Internet connection is available")
                    else:
                        logger.warning("Connected to Wi-Fi but no internet access")
                    
                    # We're connected, so just wait and check again later
                    time.sleep(60)
                else:
                    logger.info("Not connected to a Wi-Fi network")
                    
                    # Check if there are any saved connections we can connect to
                    saved_connections = ConnectionMonitor.get_saved_connections()
                    
                    if saved_connections:
                        logger.info(f"Found {len(saved_connections)} saved connections. Attempting to connect...")
                        
                        # Try to connect to each saved connection
                        connected = False
                        for connection in saved_connections:
                            logger.info(f"Trying to connect to {connection}")
                            
                            try:
                                # Attempt to activate the connection
                                os.system(f"nmcli connection up '{connection}' > /dev/null 2>&1")
                                
                                # Wait for connection to establish
                                time.sleep(10)
                                
                                # Check if we're connected
                                if NetworkManager.check_connection_status():
                                    logger.info(f"Successfully connected to {connection}")
                                    connected = True
                                    break
                            except Exception as e:
                                logger.error(f"Error connecting to {connection}: {e}")
                        
                        if connected:
                            # If we connected successfully, continue monitoring
                            continue
                        else:
                            logger.warning("Failed to connect to any saved network")
                    
                    # If we get here, we couldn't connect to any saved network
                    # So we need to start the AP mode
                    logger.info("Starting Access Point mode")
                    
                    # Setup AP mode
                    NetworkManager.setup_ap_mode()
                    
                    # Wait for a while before checking again
                    time.sleep(300)  # 5 minutes
            
            except Exception as e:
                logger.error(f"Error in connection monitor: {e}")
                time.sleep(60)
    
    @staticmethod
    def get_saved_connections():
        """
        Get a list of saved Wi-Fi connections (excluding our AP)
        
        Returns:
            list: List of connection names
        """
        try:
            import subprocess
            
            # Get all saved connections
            cmd = ["nmcli", "-t", "-f", "NAME,TYPE", "connection", "show"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            connections = []
            for line in result.stdout.splitlines():
                parts = line.split(':')
                if len(parts) >= 2 and parts[1] == "802-11-wireless" and parts[0] != "JLBMaritime":
                    connections.append(parts[0])
            
            return connections
            
        except Exception as e:
            logger.error(f"Error getting saved connections: {e}")
            return []

if __name__ == "__main__":
    # Make the script executable
    if not os.access(__file__, os.X_OK):
        os.chmod(__file__, 0o755)
    
    # Run the connection monitor
    ConnectionMonitor.run()
