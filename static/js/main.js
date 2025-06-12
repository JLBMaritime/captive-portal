// Main JavaScript file for the JLBMaritime Captive Portal

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the application
    initApp();
});

function initApp() {
    // Attach event listeners
    attachEventListeners();
    
    // Initial scan for networks
    scanNetworks();
}

function attachEventListeners() {
    // Scan button
    const scanButton = document.getElementById('scan-button');
    if (scanButton) {
        scanButton.addEventListener('click', scanNetworks);
    }
    
    // Show/hide password toggle
    const showPasswordCheckbox = document.getElementById('show-password');
    if (showPasswordCheckbox) {
        showPasswordCheckbox.addEventListener('change', togglePasswordVisibility);
    }
    
    // Connect form submission
    const connectForm = document.getElementById('connect-form');
    if (connectForm) {
        connectForm.addEventListener('submit', handleConnectFormSubmit);
    }
    
    // Close modal button
    const closeButton = document.querySelector('.close-button');
    if (closeButton) {
        closeButton.addEventListener('click', closeModal);
    }
}

// Function to scan for networks
function scanNetworks() {
    const networkList = document.getElementById('network-list');
    if (!networkList) return;
    
    // Show loading state
    networkList.innerHTML = '<div class="loading">Scanning for networks...</div>';
    
    // Make an AJAX request to scan for networks
    fetch('/scan')
        .then(response => response.json())
        .then(networks => {
            displayNetworks(networks);
        })
        .catch(error => {
            console.error('Error scanning networks:', error);
            networkList.innerHTML = '<div class="loading">Error scanning networks. Please try again.</div>';
            showToast('Error scanning networks. Please try again.', 'error');
        });
}

// Function to display networks
function displayNetworks(networks) {
    const networkList = document.getElementById('network-list');
    if (!networkList) return;
    
    if (networks.length === 0) {
        networkList.innerHTML = '<div class="loading">No networks found. Try scanning again.</div>';
        return;
    }
    
    // Sort networks by signal strength
    networks.sort((a, b) => b.signal - a.signal);
    
    // Clear the list
    networkList.innerHTML = '';
    
    // Add each network to the list
    networks.forEach(network => {
        const networkItem = document.createElement('div');
        networkItem.className = 'network-item';
        
        // Determine security type display
        let securityType = 'Open';
        if (network.security && network.security.length > 0) {
            securityType = network.security.join(', ');
        }
        
        // Determine signal class
        let signalClass = 'signal-weak';
        if (network.signal > 70) {
            signalClass = 'signal-excellent';
        } else if (network.signal > 50) {
            signalClass = 'signal-good';
        } else if (network.signal > 30) {
            signalClass = 'signal-medium';
        }
        
        networkItem.innerHTML = `
            <div class="network-info">
                <div class="network-name">
                    <div class="signal-strength ${signalClass}">
                        <div class="signal-bar bar-1"></div>
                        <div class="signal-bar bar-2"></div>
                        <div class="signal-bar bar-3"></div>
                        <div class="signal-bar bar-4"></div>
                    </div>
                    ${network.ssid}
                </div>
                <div class="network-details">
                    Security: ${securityType} | Signal: ${network.signal}%
                </div>
            </div>
            <div class="network-actions">
                <button class="action-button connect-button" data-ssid="${network.ssid}" data-security="${securityType}">
                    Connect
                </button>
            </div>
        `;
        
        // Add the network item to the list
        networkList.appendChild(networkItem);
        
        // Add event listener to the connect button
        const connectButton = networkItem.querySelector('.connect-button');
        connectButton.addEventListener('click', () => {
            openConnectModal(network.ssid, securityType !== 'Open');
        });
    });
}

// Function to open the connect modal
function openConnectModal(ssid, requiresPassword) {
    const modal = document.getElementById('connect-modal');
    const ssidInput = document.getElementById('ssid-input');
    const passwordContainer = document.getElementById('password-container');
    const passwordInput = document.getElementById('password-input');
    
    if (!modal || !ssidInput) return;
    
    // Set the SSID
    ssidInput.value = ssid;
    
    // Show/hide password field based on security
    if (passwordContainer) {
        passwordContainer.style.display = requiresPassword ? 'block' : 'none';
    }
    
    // Clear the password field
    if (passwordInput) {
        passwordInput.value = '';
    }
    
    // Show the modal
    modal.classList.remove('hidden');
}

// Function to close the connect modal
function closeModal() {
    const modal = document.getElementById('connect-modal');
    if (modal) {
        modal.classList.add('hidden');
    }
}

// Function to toggle password visibility
function togglePasswordVisibility() {
    const passwordInput = document.getElementById('password-input');
    const showPasswordCheckbox = document.getElementById('show-password');
    
    if (!passwordInput || !showPasswordCheckbox) return;
    
    passwordInput.type = showPasswordCheckbox.checked ? 'text' : 'password';
}

// Function to handle the connect form submission
function handleConnectFormSubmit(event) {
    event.preventDefault();
    
    const ssidInput = document.getElementById('ssid-input');
    const passwordInput = document.getElementById('password-input');
    const passwordContainer = document.getElementById('password-container');
    
    if (!ssidInput) return;
    
    const ssid = ssidInput.value.trim();
    if (!ssid) {
        showToast('Please select a network.', 'error');
        return;
    }
    
    // Check if password is required and provided
    const requiresPassword = passwordContainer && passwordContainer.style.display !== 'none';
    const password = passwordInput ? passwordInput.value : '';
    
    if (requiresPassword && !password) {
        showToast('Please enter the network password.', 'error');
        return;
    }
    
    // Disable form elements during connection attempt
    const connectButton = document.querySelector('#connect-form button[type="submit"]');
    if (connectButton) {
        connectButton.disabled = true;
        connectButton.textContent = 'Connecting...';
    }
    
    // Make an AJAX request to connect to the network
    fetch('/connect', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            ssid: ssid,
            password: password
        }),
    })
    .then(response => response.json())
    .then(data => {
        // Re-enable the connect button
        if (connectButton) {
            connectButton.disabled = false;
            connectButton.textContent = 'Connect';
        }
        
        if (data.success) {
            showToast('Successfully connected to ' + ssid, 'success');
            closeModal();
            
            // Redirect to success page after short delay
            setTimeout(() => {
                window.location.href = '/success';
            }, 2000);
        } else {
            showToast(data.message || 'Failed to connect. Please check your password and try again.', 'error');
        }
    })
    .catch(error => {
        console.error('Error connecting to network:', error);
        
        // Re-enable the connect button
        if (connectButton) {
            connectButton.disabled = false;
            connectButton.textContent = 'Connect';
        }
        
        showToast('Error connecting to network. Please try again.', 'error');
    });
}

// Function to show a toast notification
function showToast(message, type = 'info') {
    // Create toast container if it doesn't exist
    let toastContainer = document.getElementById('toast-container');
    
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        document.body.appendChild(toastContainer);
    }
    
    // Create the toast element
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    
    // Add the toast to the container
    toastContainer.appendChild(toast);
    
    // Remove the toast after animation completes
    setTimeout(() => {
        toast.remove();
    }, 3000);
}
