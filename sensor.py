#!/usr/bin/env python
import serial
import sys, time

class SensorSerialError(serial.SerialException): pass
class Sensor:
    SENSOR_NORMALLY_ON = bytearray([0x52, 0x42, 0x0a, 0x00, 0x02, 0x11, 0x51, 0x01, 0x00, 0, 255, 0])
    SENSOR_NORMALLY_OFF = bytearray([0x52, 0x42, 0x0a, 0x00, 0x02, 0x11, 0x51, 0x00, 0x00, 0, 0, 0])
    SENSOR_READ = bytearray([0x52, 0x42, 0x05, 0x00, 0x01, 0x21, 0x50])
    VALID_DATALEN = 58
    def __init__(self, device='/dev/ttyUSB0', speed=115200, databit=serial.EIGHTBITS, parity=serial.PARITY_NONE):
        self.serial = serial.Serial(device, speed, databit, parity)
        self.isopened = False
    def _get_command(self, buf):
        length = len(buf)
        crc = 0xFFFF
        for i in range(length):
            crc = crc ^ buf[i]
            for i in range(8):
                carrayFlag = crc & 1
                crc = crc >> 1
                if (carrayFlag == 1):
                    crc = crc ^ 0xA001
        crcH = crc >> 8
        crcL = crc & 0x00FF
        return buf + (bytearray([crcL, crcH]))
    def isopen(self):
        return (self.isopened and self.serial.is_open)
    def open(self):
        command = self._get_command(self.SENSOR_NORMALLY_ON)
        if self.isopen():
            return
        try:
            self.serial.write(command)
            time.sleep(0.5)
            self.isopened = True
            return self.serial.read(self.serial.inWaiting())
        except serial.SerialException as e:
            raise SensorSerialError(e)
    def close(self):
        command = self._get_command(self.SENSOR_NORMALLY_OFF)
        if not self.isopen():
            return
        try:
            self.serial.write(command)
            time.sleep(0.5)
            self.isopened = False
            return self.serial.read(self.serial.inWaiting())
        except serial.SerialException:
            # Retry
            self.close()
        return
    def read(self):
        try:
            command = self._get_command(self.SENSOR_READ)
            self.serial.write(command)
            time.sleep(0.5)
            data = self.serial.read(self.serial.inWaiting())
            if len(data) == self.VALID_DATALEN:
                return data
            return None
        except serial.SerialException:
            self.close()

if __name__ == "__main__":
    sen = Sensor()
    sen.open()
    while sen.isopen():
        data = sen.read()
        print(json.dumps(data))
