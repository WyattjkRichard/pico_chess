import os
import network
import time
import socket


def save_credentials(ssid, password):
    """
    save_credentials:
    Writes SSID and password to wifi_config.txt
    Returns: nothing
    """
    with open("wifi_config.txt", "w") as f:
        f.write(f"{ssid}\n{password}")


def load_credentials():
    """
    load_credentials:
    Reads SSID and password from wifi_config.txt
    Returns: SSID and password
    """
    if "wifi_config.txt" in os.listdir():
        with open("wifi_config.txt", "r") as f:
            ssid, password = f.read().splitlines()
        return ssid, password
    return None, None


def connect_to_wifi(ssid, password):
    """
    connect_to_wifi:
    Connects to a given SSID using the given password
    Returns: true if able to connect, else returns false
    """
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    # Wait for connection
    max_wait = 10
    while max_wait > 0:
        if wlan.isconnected():
            # successfully connected
            return True
        max_wait -= 1
        print("Attempting to connect...")
        time.sleep(1)
    
    print("Failed to connect to {ssid}.")
    print("Current network status:", wlan.status())
    return False


def url_decode(encoded_str):
    """
    url_decode:
    Decodes url
    Returns: decoded string
    """
    decoded_str = ""
    i = 0
    while i < len(encoded_str):
        if encoded_str[i] == '%':
            decoded_str += chr(int(encoded_str[i+1:i+3], 16))
            i += 3
        elif encoded_str[i] == '+':
            decoded_str += ' '
            i += 1
        else:
            decoded_str += encoded_str[i]
            i += 1
    return decoded_str


def start_access_point():
    """
    start_access_point:
    Creates an access point
    Returns: Access point IP
    """
    ap = network.WLAN(network.AP_IF)
    ap.config(essid="Smart Chess Setup", password="smartchess")
    ap.active(True)
    
    while not ap.active():
        pass
    
    print('Access Point active with IP:', ap.ifconfig())
    return ap.ifconfig()[0]


def scan_networks():
    """
    scan_networks:
    Scans for available SSID's
    Returns: scanned networks
    """
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    return wlan.scan()


def start_web_server():
    """
    start_web_server:
    Displays list of available SSID's
    Returns: scanned networks
    """

    ssid_list = scan_networks()
    
    # Build HTML page with available SSIDs
    html = """<!DOCTYPE html>
    <html>
    <head><title>Pico W Wi-Fi Setup</title></head>
    <body>
        <form action="/" method="POST">
        <label for="ssid">Select Wi-Fi Network:</label>
        <select name="ssid" id="ssid">"""
    
    for ssid in ssid_list:        
        try:
            ssid_name = ssid[0].decode("utf-8")
        except UnicodeDecodeError:
            continue  # Skip SSIDs that can't be decoded
        
        
        if ssid_name.strip() and not any(c in ssid_name for c in ['\x00', '\xFF']):  # Check if SSID is not empty or just whitespace
            html += f'<option value="{ssid_name}">{ssid_name}</option>'
    
    html += """
        </select><br><br>
        Password: <input type="password" name="password"><br>
        <input type="submit" value="Submit">
        </form>
    </body>
    </html>
    """
    
    addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(1)
    
    print("Web server started, waiting for connections...")
    
    while True:
        cl, addr = s.accept()
        print("Client connected from", addr)
        request = cl.recv(1024)
        
        # Handle HTTP request
        request_str = request.decode("utf-8")
        if "POST" in request_str:
            
            # Extract SSID and Password
            params = request_str.split("\r\n")[-1]
            params_dict = {p.split("=")[0]: p.split("=")[1] for p in params.split("&")}
            
            # Handle the case where either SSID or password is missing
            if "ssid" not in params_dict or "password" not in params_dict:
                cl.send("HTTP/1.1 400 Bad Request\nContent-Type: text/html\nConnection: close\n\n")
                cl.send("<h1>Error: Missing SSID or Password</h1>")
                cl.close()
                continue

            cl.send("HTTP/1.1 200 OK\nContent-Type: text/html\nConnection: close\n\n")
            cl.send("<h1>Connecting...</h1>")

            # Manually URL decode SSID and Password
            ssid = url_decode(params_dict["ssid"])
            password = url_decode(params_dict["password"])
            
            # Try to connect with provided credentials
            if connect_to_wifi(ssid, password):
                save_credentials(ssid, password)
                cl.send("<h1>Connected</h1>")
                cl.close()
                break
            else:
                cl.send("<h1>Connection Failed. Please try again.</h1><a href='/'>Back to Setup</a>")
                cl.close()
                continue
        
        cl.send("HTTP/1.1 200 OK\nContent-Type: text/html\nConnection: close\n\n")
        cl.send(html)
        cl.close()
    
    
try:
    ssid, password = load_credentials()
    if ssid and connect_to_wifi(ssid, password):
        print(f"Successfully connected to {ssid}")
    else:
        print("Starting access point for setup...")
        start_access_point()
        start_web_server()
        print("Wi-Fi configuration completed.")
except KeyboardInterrupt:
    machine.reset()