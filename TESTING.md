# JLBMaritime Captive Portal Testing Instructions

This document provides instructions for testing the JLBMaritime Captive Portal after installation.

## Basic Functionality Tests

### 1. Verify Services Are Running

After installation, check that both services are running properly:

```bash
sudo systemctl status captive-portal.service
sudo systemctl status connection-monitor.service
```

Look for "active (running)" status for both services. If they're not running, you can start them with:

```bash
sudo systemctl start captive-portal.service
sudo systemctl start connection-monitor.service
```

### 2. Check Access Point

From another device (smartphone, laptop, or tablet):

1. Look for the "JLBMaritime" Wi-Fi network in your list of available networks
2. Connect to it using the password "Admin"
3. Your device should automatically redirect to the captive portal
4. If not redirected automatically, open a browser and navigate to http://10.42.0.1:5000

### 3. Test Wi-Fi Connection

Once the captive portal is open:

1. Wait for the list of available Wi-Fi networks to load
2. Select your home/office Wi-Fi network from the list
3. Enter the correct password when prompted
4. Click "Connect"
5. You should be redirected to the success page showing connection details
6. Your AIS receiver/server should now be connected to your Wi-Fi network

## Advanced Testing

### 1. Test Automatic Reconnection

After successfully connecting to a Wi-Fi network:

1. Restart the Raspberry Pi:
   ```bash
   sudo reboot
   ```

2. After reboot, check if it automatically connects to the configured network:
   ```bash
   nmcli connection show --active
   ```
   
3. You should see your Wi-Fi network listed as active, not the JLBMaritime AP

### 2. Test Fallback to AP Mode

To test the fallback mechanism:

1. Disconnect from all known Wi-Fi networks (e.g., turn off your router or move out of range)
2. Restart the Raspberry Pi:
   ```bash
   sudo reboot
   ```

3. After reboot, check from another device if the "JLBMaritime" network appears
4. The system should have created the access point since no known networks were available

### 3. Test Connection After Power Loss

To simulate power loss:

1. Connect to a Wi-Fi network via the captive portal
2. Unplug the Raspberry Pi power cable
3. Wait 10 seconds
4. Reconnect power
5. The Pi should automatically reconnect to the known Wi-Fi network

## Troubleshooting

### Check Logs

If you encounter issues, check the logs:

```bash
sudo tail -f /var/log/captive-portal.log
```

This will display real-time logs that can help diagnose any issues.

### Common Issues and Solutions

1. **No JLBMaritime Network Appears**
   - Ensure the installation completed without errors
   - Check that the Wi-Fi adapter is working: `rfkill list`
   - Verify the Wi-Fi adapter is not blocked: `sudo rfkill unblock wifi`
   - Check which wireless interfaces are available: `ip link show | grep -i wlan`
   - Restart the NetworkManager service: `sudo systemctl restart NetworkManager`
   - If logs show `ERROR - Error setting up AP mode`, try the following:
     ```bash
     # Check if the AP connection exists
     sudo nmcli connection show | grep JLBMaritime
     
     # If it exists, try deleting it and recreating
     sudo nmcli connection delete JLBMaritime
     
     # Find your wireless interface name
     sudo ip link show | grep wlan
     
     # Create the AP with the specific interface name (replace wlan0 with your interface)
     sudo nmcli connection add type wifi ifname wlan0 con-name "JLBMaritime" autoconnect yes ssid "JLBMaritime" mode ap ipv4.method shared ipv4.addresses "10.42.0.1/24" wifi-sec.key-mgmt wpa-psk wifi-sec.psk "Admin"
     
     # Activate the connection
     sudo nmcli connection up JLBMaritime
     ```
     
   - Check if your wireless adapter supports AP mode:
     ```bash
     sudo iw list | grep -A 10 "Supported interface modes"
     ```
     Look for "AP" in the list of supported modes.

2. **Cannot Connect to JLBMaritime Network**
   - Verify you're using the correct password ("Admin")
   - Try forgetting the network on your device and reconnecting
   - Restart the access point: `sudo nmcli connection down JLBMaritime && sudo nmcli connection up JLBMaritime`

3. **Captive Portal Not Showing**
   - Try navigating directly to http://10.42.0.1:5000
   - Check if the Flask service is running: `sudo systemctl status captive-portal.service`
   - Check for errors in the log: `sudo tail -f /var/log/captive-portal.log`

4. **Cannot Connect to Wi-Fi Network**
   - Verify the password is correct
   - Check signal strength (move closer to the router)
   - Ensure the Wi-Fi network is operational
   - Check for encryption compatibility issues

5. **System Not Reconnecting After Reboot**
   - Check if the connection was saved: `nmcli connection show`
   - Verify the connection-monitor service is running: `sudo systemctl status connection-monitor.service`
   - Check logs for connection errors: `sudo tail -f /var/log/captive-portal.log`
