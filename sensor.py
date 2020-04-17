#!/usr/bin/env python
import serial
import sys, time

TO_INT = lambda s: int(s.encode('hex'), 16)
class SensorSerialError(serial.SerialException): pass
class Sensor:
    SENSOR_NORMALLY_ON = bytearray([0x52, 0x42, 0x0a, 0x00, 0x02, 0x11, 0x51, 0x01, 0x00, 0, 255, 0])
    SENSOR_NORMALLY_OFF = bytearray([0x52, 0x42, 0x0a, 0x00, 0x02, 0x11, 0x51, 0x00, 0x00, 0, 0, 0])
    SENSOR_READ = bytearray([0x52, 0x42, 0x05, 0x00, 0x01, 0x21, 0x50])
    VALID_DATALEN = 58
    CACHE_TTL = 3.0
    def __init__(self, device='/dev/ttyUSB0', speed=115200, databit=serial.EIGHTBITS, parity=serial.PARITY_NONE):
        self.serial = serial.Serial(device, speed, databit, parity)
        self.isopened = False
        self.data = None
        self.lastmodified = 0.0
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
    def _read(self):
        if not self.isopen():
            self.open()
        try:
            command = self._get_command(self.SENSOR_READ)
            self.serial.write(command)
            time.sleep(0.5)
            data = self.serial.read(self.serial.inWaiting())
            if len(data) == self.VALID_DATALEN:
                self.data = data
                self.lastmodified = time.time()
        except serial.SerialException:
            self.close()
    def _renew(self):
        if self.data and (self.lastmodified + self.CACHE_TTL) > time.time():
            return
        self._read()
    def get_temperature(self):
        self._renew()
        return int('{:x}{:02x}'.format(TO_INT(self.data[9]), TO_INT(self.data[8])), 16) / 100.0
    def get_relative_humidity(self):
        self._renew()
        return int('{:x}{:02x}'.format(TO_INT(self.data[11]), TO_INT(self.data[10])), 16) / 100.0
    def get_ambient_light(self):
        self._renew()
        return int('{:x}{:02x}'.format(TO_INT(self.data[13]), TO_INT(self.data[12])), 16)
    def get_barometric_pressure(self):
        self._renew()
        return int('{:x}{:02x}{:02x}{:02x}'.format(TO_INT(self.data[17]), TO_INT(self.data[16]), TO_INT(self.data[15]), TO_INT(self.data[14])), 16) / 1000.0
    def get_sound_noise(self):
        self._renew()
        return int('{:x}{:02x}'.format(TO_INT(self.data[19]), TO_INT(self.data[18])), 16) / 100.0
    def get_eTVOC(self):
        self._renew()
        return int('{:x}{:02x}'.format(TO_INT(self.data[21]), TO_INT(self.data[20])), 16)
    def get_eCO2(self):
        self._renew()
        return int('{:x}{:02x}'.format(TO_INT(self.data[23]), TO_INT(self.data[22])), 16)
    def get_discomfort_index(self):
        self._renew()
        return int('{:x}{:02x}'.format(TO_INT(self.data[25]), TO_INT(self.data[24])), 16) / 100.0
    def get_heat_stroke(self):
        self._renew()
        return int('{:x}{:02x}'.format(TO_INT(self.data[27]), TO_INT(self.data[26])), 16) / 100.0
    def get_vibration_information(self):
        self._renew()
        return int('{:x}'.format(TO_INT(self.data[28])), 16)
    def get_si_value(self):
        self._renew()
        return int('{:x}{:02x}'.format(TO_INT(self.data[30]), TO_INT(self.data[29])), 16) / 10.0
    def get_pga(self):
        self._renew()
        return int('{:x}{:02x}'.format(TO_INT(self.data[32]), TO_INT(self.data[31])), 16) / 10.0
    def get_seismic_intensity(self):
        self._renew()
        return int('{:x}{:02x}'.format(TO_INT(self.data[34]), TO_INT(self.data[33])), 16) / 1000.0

if __name__ == "__main__":
    sen = Sensor()
    print("Temperature: {}".format(sen.get_temperature()))
    print("RelativeHumidity: {}".format(sen.get_relative_humidity()))
    print("AmbientLight: {}".format(sen.get_ambient_light()))
    print("BarometicPressure: {}".format(sen.get_barometric_pressure()))
    print("SoundNoise: {}".format(sen.get_sound_noise()))
    print("eTVOC: {}".format(sen.get_eTVOC()))
    print("eCO2: {}".format(sen.get_eCO2()))
    print("DiscomfortIndex: {}".format(sen.get_discomfort_index()))
    print("HeatStroke: {}".format(sen.get_heat_stroke()))
    print("VibrationInformation: {}".format(sen.get_vibration_information()))
    print("PGA: {}".format(sen.get_pga()))
    print("SeismicIntensity: {}".format(sen.get_seismic_intensity()))
