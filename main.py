import time
from machine import Pin, I2C
import ssd1306
from max6675 import MAX6675


def init_oled():
    i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400000)
    return ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3c)


oled = init_oled()

so = Pin(15, Pin.IN)
cs = Pin(14, Pin.OUT)
sck = Pin(13, Pin.OUT)
max_sensor = MAX6675(sck, cs, so)


while True:
    temps = []
    for i in range(10):
        temps.append(max_sensor.read())
        time.sleep(0.1)
    avg = sum(temps) / len(temps)
    
    oled.fill(0)
    oled.text(f"AVG: {avg:.2f}C", 0, 0)
    oled.text(f"T:   {temps[-1]:.2f}C", 0, 10)
    oled.show()