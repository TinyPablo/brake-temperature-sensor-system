import time
from machine import Pin, I2C
import ssd1306
from max6675 import MAX6675


def init_oled():
    i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400000)
    return ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3c)


oled = init_oled()

so  = Pin(15, Pin.IN)
cs  = Pin(14, Pin.OUT)
sck = Pin(13, Pin.OUT)
max_sensor = MAX6675(sck, cs, so)

# Running totals for all-time average
all_sum   = 0
all_count = 0

# Session extremes
ses_max = None
ses_min = None

# Bar represents 0 – 200 °C
BAR_MAX   = 200
BAR_X, BAR_Y = 0, 38
BAR_W, BAR_H = 128, 14
INNER_W       = BAR_W - 4   # 2px padding each side

while True:
    # --- Read 10 samples over ~1 s ---
    temps = []
    for _ in range(10):
        temps.append(max_sensor.read())
        time.sleep(0.1)

    # Current reading = avg of this batch (rounded, no float on screen)
    now = round(sum(temps) / len(temps))

    # Feed all samples into the running all-time average
    for t in temps:
        all_sum   += t
        all_count += 1

    av = round(all_sum / all_count)

    # Update session max / min
    if ses_max is None or now > ses_max:
        ses_max = now
    if ses_min is None or now < ses_min:
        ses_min = now

    # --- Bar fill: based on all-time average, clamped to 0-200 ---
    fill_ratio = min(1.0, max(0.0, av / BAR_MAX))
    fill_px    = int(fill_ratio * INNER_W)

    # --- Draw ---
    oled.fill(0)

    # Row 1  e.g. "AV 215   MX 387"
    oled.text(f"AV {av:<4} MX {ses_max}", 0, 0)

    # Row 2  e.g. "MN 42    NW 220"
    oled.text(f"MN {ses_min:<4} NW {now}", 0, 12)

    # Scale labels above the bar
    oled.text("0", 0, 28)
    oled.text("200C", 96, 28)

    # Bar outline
    oled.rect(BAR_X, BAR_Y, BAR_W, BAR_H, 1)

    # Bar fill (2px padding inside outline)
    if fill_px > 0:
        oled.fill_rect(BAR_X + 2, BAR_Y + 2, fill_px, BAR_H - 4, 1)

    oled.show()