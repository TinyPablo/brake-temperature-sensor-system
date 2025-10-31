import time
import socket
from machine import Pin, I2C
import ssd1306
import network
import secrets
from max6675 import MAX6675

SSID = secrets.SSID
PASSWORD = secrets.PASSWORD
SERVER_IP = "192.168.1.100"
SERVER_PORT = 5000

def init_oled():
    i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400000)
    return ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3c)

def connect_wifi(oled):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    dot_count = 0
    while not wlan.isconnected():
        oled.fill(0)
        oled.text('.' * dot_count, 0, 0)
        oled.show()
        dot_count = (dot_count % 3) + 1
        time.sleep(0.3)
    ip = wlan.ifconfig()[0]
    print("WiFi Connected - IP:", ip)
    return wlan

def create_socket():
    s = socket.socket()
    addr = socket.getaddrinfo(SERVER_IP, SERVER_PORT)[0][-1]
    s.connect(addr)
    return s

oled = init_oled()
wlan = connect_wifi(oled)
sock = None


so1 = Pin(15, Pin.IN)
cs1 = Pin(14, Pin.OUT)
sck1 = Pin(13, Pin.OUT)
max_sensor1 = MAX6675(sck1, cs1, so1)

so2 = Pin(12, Pin.IN)
cs2 = Pin(11, Pin.OUT)
sck2 = Pin(10, Pin.OUT)
max_sensor2 = MAX6675(sck2, cs2, so2)

while True:
    temp1 = max_sensor1.read()
    temp2 = max_sensor2.read()
    tstamp = time.time()
    data = f"{tstamp},{temp1:.2f},{temp2:.2f}\n"
    
    print(data.strip())
    
    oled.fill(0)
    oled.text(f"T1:{temp1:.2f}C", 0, 0)
    oled.text(f"T2:{temp2:.2f}C", 0, 10)
    oled.show()
    
    if sock is None:
        try:
            sock = create_socket()
            status = "Server: OK"
            
        except Exception as e:
            status = "Server: NOK"
            
    else:
        try:
            sock.send(data.encode())
            status = "Server: OK"
            
        except OSError as e:
            sock = None
            status = "Server: NOK"
    
    oled.text(status, 0, 20)
    oled.show()
    time.sleep(1)