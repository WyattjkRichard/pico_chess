import network
import socket

ssid = "Smart Chess"
password = "123456789"

def connect():
    # Set up Access Point
    ap = network.WLAN(network.AP_IF)
    ap.config(essid=ssid, password=password)  # Set your desired SSID here
    ap.active(True)

    while not ap.active():
        pass

    print('Access Point active with IP:', ap.ifconfig())
    
    
def open_socket():
    # Open a socket
    address = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    connection = socket.socket()
    connection.bind(address)
    connection.listen(5)
    print('Listening on', address)
    return connection
    
    
def webpage():
    #Template HTML
    html = """<!DOCTYPE html>
            <html>
            <head>
                <title>Pico W Webpage</title>
            </head>
            <body>
                <h1>Hello from Pico W!</h1>
            </body>
            </html>
            """
    return str(html)


def serve(connection, html):
    while True:
        cl, addr = connection.accept()
        print('Client connected from', addr)
        cl_file = cl.makefile('rwb', 0)
        while True:
            line = cl_file.readline()
            if not line or line == b'\r\n':
                break
        cl.send(html)
        cl.close()
    
    
try:
    connect()
    connection = open_socket()
    html = webpage()
    serve(connection, html)
except KeyboardInterrupt:
    machine.reset()