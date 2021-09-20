#!/usr/bin/python
import bakebit_128_64_oled as oled
import smbus
import threading, queue
import time
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

class NanoHatOled ():
    WIDTH = oled.SeeedOLED_Width
    HEIGHT = oled.SeeedOLED_Height
    FONT_TT_BOLD = '/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf'
    FONT_TT_NORMAL = '/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf'
    def __init__(self):
        self.image = Image.new('1', (self.WIDTH, self.HEIGHT))
        self.draw = ImageDraw.Draw(self.image)
        self.queue = queue.Queue()
        self.oled_init()
    def oled_init(self):
        oled.init()
        oled.setNormalDisplay()
        oled.setHorizontalMode()
    def oled_clear(self):
        oled.clearDisplay()
    def oled_close(self):
        oled.sendCommand(oled.SeeedOLED_Display_Off_Cmd)
        for j in range(8):
            oled.setTextXY(0,j)
            for i in range(16):
                oled.putChar(' ')
        oled.setTextXY(0, 0)
    def font_bold(self, size=0):
        return ImageFont.truetype(self.FONT_TT_BOLD, size)
    def font_normal(self, size=0):
        return ImageFont.truetype(self.FONT_TT_NORMAL, size)
    def put_image(self, deg, humi, eco2, baro):
        self.draw.rectangle((0,0,self.WIDTH,self.HEIGHT), outline=0, fill=0)
        self.draw.text((2,2), "{:3.1f}".format(deg), font=self.font_bold(size=22), fill=255)
        self.draw.text((62,4), "{:3.1f} %".format(humi), font=self.font_normal(size=18), fill=255)
        self.draw.text((2,24), "{:4d} ppm".format(eco2), font=self.font_normal(size=16), fill=255)
        self.draw.text((2,42), "{:.1f} hPa".format(baro), font=self.font_normal(size=16), fill=255)
        self.queue.put(self.image)
    def _draw_loop(self):
        while True:
            image = self.queue.get()
            oled.drawImage(image)
            oled.setBrightness(0)
            self.queue.task_done()
    def start(self):
        th = threading.Thread(target=self._draw_loop)
        th.setDaemon(True)
        th.start()

if __name__ == "__main__":

    screen = NanoHatOled()
    screen.start()

    screen.put_image(11.0, 11.0, 1111, 1111.0)
    screen.queue.join()
    print("After tasks 1")
    time.sleep(5)

    screen.put_image(22.0, 22.0, 2222, 2222.0)
    screen.queue.join()
    print("After tasks 2")
    time.sleep(5)

    screen.put_image(33.0, 33.0, 3333, 3333.0)
    screen.queue.join()
    print("After tasks 3")
    time.sleep(5)

    screen.put_image(44.0, 44.0, 4444, 4444.0)
    screen.queue.join()
    print("After tasks 4")
    time.sleep(5)

    screen.oled_close()
