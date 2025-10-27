import time
from machine import Pin, I2C # type: ignore

import ssd1306 # type: ignore
from max6675 import MAX6675 # type: ignore


def init_oled():
    i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400000)
    oled = ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3c)
    return oled


oled = init_oled()


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
    
    temp1_text = f"{temp1:.2f}C"
    temp2_text = f"{temp2:.2f}C"
    temp_difference = f"{(abs(temp2-temp1)):.2f}C"
    
    print(temp1_text)
    print(temp2_text)
    print(temp_difference)
    print()
    
    oled.fill(0)
    
    oled.text(temp1_text, 0, 00)
    oled.text(temp2_text, 0, 10)
    oled.text(temp_difference, 0, 20)
    
    oled.show()
    
    time.sleep(1)