#!/usr/bin/env python3
# app.py - Flask application for JLBMaritime Captive Portal

from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import logging
import socket
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
logger = logging.getLogger("captive_portal")

# Create Flask app
app = Flask(__name__)

# Initialize state
connection_info = None

@app.route('/', methods=['GET'])
def index():
    """
    Main captive portal page
    """
    # For Apple/Google/Windows captive portal detection
    user_agent = request.headers.get('User-Agent', '').lower()
    
    if 'captiveportal' in user_agent or 'captivenetworksupport' in user_agent:
        logger.info("Captive portal detection request detected")
        return "Success"
    
    # For any external hostname, redirect to captive portal
    if request.host != "10.42.0.1:5000" and request.host != "localhost:5000":
        logger.info(f"Redirecting request from {request.host} to captive portal")
        return redirect("http://10.42.0.1:5000/", code=302)
    
    return render_template('index.html')

@app.route('/scan', methods=['GET'])
def scan_networks():
    """
    Scan for available Wi-Fi networks
    """
    networks = NetworkManager.scan_networks()
    return jsonify(networks)

@app.route('/connect', methods=['POST'])
def connect_to_network():
    """
    Connect to a Wi-Fi network
    """
    global connection_info
    
    data = request.json
    if not data or 'ssid' not in data:
        return jsonify({"success": False, "message": "SSID is required"})
    
    ssid = data['ssid']
    password = data.get('password', '')
    
    logger.info(f"Attempting to connect to network: {ssid}")
    
    success, result = NetworkManager.connect_to_network(ssid, password)
    
    if success:
        # Store connection info for success page
        connection_info = {
            'ssid': ssid,
            'ip_address': result.get('ip_address', 'Unknown'),
            'signal_strength': result.get('signal_strength', 0)
        }
        
        # Restore normal DNS settings
        AccessPoint.restore_dnsmasq()
        
        return jsonify({"success": True, "message": "Successfully connected", "data": result})
    else:
        return jsonify({"success": False, "message": result.get('message', 'Failed to connect')})

@app.route('/success', methods=['GET'])
def success():
    """
    Success page after successful connection
    """
    global connection_info
    
    if not connection_info:
        # If connection_info is not available, get current connection
        active_connection = NetworkManager.get_active_connection()
        if active_connection:
            connection_info = {
                'ssid': active_connection.get('ssid', 'Unknown'),
                'ip_address': active_connection.get('ip_address', 'Unknown'),
                'signal_strength': active_connection.get('signal_strength', 0)
            }
        else:
            # Redirect to index if not connected
            return redirect(url_for('index'))
    
    return render_template(
        'success.html',
        ssid=connection_info.get('ssid', 'Unknown'),
        ip_address=connection_info.get('ip_address', 'Unknown'),
        signal_strength=connection_info.get('signal_strength', 0)
    )

@app.route('/generate_204', methods=['GET'])
@app.route('/ncsi.txt', methods=['GET'])
@app.route('/connecttest.txt', methods=['GET'])
@app.route('/redirect', methods=['GET'])
def captive_portal_check():
    """
    Endpoints for various captive portal detection mechanisms
    """
    logger.info(f"Captive portal check from {request.path}")
    return redirect(url_for('index'))

@app.route('/hotspot-detect.html', methods=['GET'])
@app.route('/library/test/success.html', methods=['GET'])
def apple_captive_portal_check():
    """
    Endpoints for Apple captive portal detection
    """
    logger.info(f"Apple captive portal check from {request.path}")
    return render_template('index.html')

@app.errorhandler(404)
def page_not_found(e):
    """
    Handle 404 errors by redirecting to index
    """
    logger.info(f"404 error for {request.path}, redirecting to index")
    return redirect(url_for('index'))

def get_ip_address():
    """
    Get the IP address of the wlan0 interface
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "10.42.0.1"  # Default fallback

def initialize():
    """
    Initialize the application
    """
    # Set up access point mode if not connected to a Wi-Fi network
    if not NetworkManager.check_connection_status():
        logger.info("Not connected to any Wi-Fi network, setting up access point mode")
        NetworkManager.setup_ap_mode()
        AccessPoint.setup()
    else:
        logger.info("Already connected to a Wi-Fi network, keeping client mode")

if __name__ == "__main__":
    # Make the script executable
    if not os.access(__file__, os.X_OK):
        os.chmod(__file__, 0o755)
    
    # Initialize
    initialize()
    
    # Run the Flask app
    ip = get_ip_address()
    logger.info(f"Starting Flask application on {ip}:5000")
    app.run(host=ip, port=5000, debug=False)
