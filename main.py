#!/usr/bin/python
import sys, os
import time
import serial
import urllib2
import json
import traceback
import datetime, time

SENSOR_SERIAL_DEVICE = os.environ.get('SENSOR_SERIAL_DEVICE', '/dev/ttyUSB0')
SENSOR_NORMALLY_OFF = 0x00
SENSOR_NORMALLY_ON = 0x01
SENSOR_VALID_DATALEN = 58

MACHINIST_URL = "https://gw.machinist.iij.jp/endpoint"
MACHINIST_APIKEY = os.environ.get('MACHINIST_APIKEY', '')
MACHINIST_NAMESPACE = os.environ.get('MACHINIST_NAMESPACE', 'env_sensor')
MACHINIST_SEND_METRICS = os.environ.get('MACHINIST_SEND_METRICS', '')

def calc_crc(buf, length):
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
    return (bytearray([crcL, crcH]))

def send_machinist(data, time_measured):
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + MACHINIST_APIKEY
    }
    content = {
        "agent": "env_sensor",
        "metrics": []
    }
    to_int = lambda s: int(s.encode('hex'), 16)
    timestamp = int(time.mktime(time_measured.timetuple()))
    allow_metrics = MACHINIST_SEND_METRICS.split()
    if 'temperature' in allow_metrics:
        content['metrics'].append(
            {
                "name": "temperature",
                "namespace": MACHINIST_NAMESPACE,
                "data_point": {
                    "value": int('{:x}{:02x}'.format(to_int(data[9]), to_int(data[8])), 16) / 100.0,
                    "timestamp": timestamp
                }
            }
        )
    if 'relative_humidity' in allow_metrics:
        content['metrics'].append(
            {
                "name": "relative_humidity",
                "namespace": MACHINIST_NAMESPACE,
                "data_point": {
                    "value": int('{:x}{:02x}'.format(to_int(data[11]), to_int(data[10])), 16) / 100.0,
                    "timestamp": timestamp
                }
            }
        )
    if 'ambient_light' in allow_metrics:
        content['metrics'].append(
            {
                "name": "ambient_light",
                "namespace": MACHINIST_NAMESPACE,
                "data_point": {
                    "value": int('{:x}{:02x}'.format(to_int(data[13]), to_int(data[12])), 16),
                    "timestamp": timestamp
                }
            }
        )
    if 'barometric_pressure' in allow_metrics:
        content['metrics'].append(
            {
                "name": "barometric_pressure",
                "namespace": MACHINIST_NAMESPACE,
                "data_point": {
                    "value": int('{:x}{:02x}{:02x}{:02x}'.format(to_int(data[17]), to_int(data[16]), to_int(data[15]), to_int(data[14])), 16) / 1000.0,
                    "timestamp": timestamp
                }
            }
        )
    if 'sound_noise' in allow_metrics:
        content['metrics'].append(
            {
                "name": "sound_noise",
                "namespace": MACHINIST_NAMESPACE,
                "data_point": {
                    "value": int('{:x}{:02x}'.format(to_int(data[19]), to_int(data[18])), 16) / 100.0,
                    "timestamp": timestamp
                }
            }
        )
    if 'eTVOC' in allow_metrics:
        content['metrics'].append(
            {
                "name": "eTVOC",
                "namespace": MACHINIST_NAMESPACE,
                "data_point": {
                    "value": int('{:x}{:02x}'.format(to_int(data[21]), to_int(data[20])), 16),
                    "timestamp": timestamp
                }
            }
        )
    if 'eCO2' in allow_metrics:
        content['metrics'].append(
            {
                "name": "eCO2",
                "namespace": MACHINIST_NAMESPACE,
                "data_point": {
                    "value": int('{:x}{:02x}'.format(to_int(data[23]), to_int(data[22])), 16),
                    "timestamp": timestamp
                }
            }
        )
    if 'discomfort_index' in allow_metrics:
        content['metrics'].append(
            {
                "name": "discomfort_index",
                "namespace": MACHINIST_NAMESPACE,
                "data_point": {
                    "value": int('{:x}{:02x}'.format(to_int(data[25]), to_int(data[24])), 16) / 100.0,
                    "timestamp": timestamp
                }
            }
        )
    if 'heat_stroke' in allow_metrics:
        content['metrics'].append(
            {
                "name": "heat_stroke",
                "namespace": MACHINIST_NAMESPACE,
                "data_point": {
                    "value": int('{:x}{:02x}'.format(to_int(data[27]), to_int(data[26])), 16) / 100.0,
                    "timestamp": timestamp
                }
            }
        )
    if 'vibration_information' in allow_metrics:
        content['metrics'].append(
            {
                "name": "vibration_information",
                "namespace": MACHINIST_NAMESPACE,
                "data_point": {
                    "value": int('{:x}'.format(to_int(data[28])), 16),
                    "timestamp": timestamp
                }
            }
        )
    if 'si_value' in allow_metrics:
        content['metrics'].append(
            {
                "name": "si_value",
                "namespace": MACHINIST_NAMESPACE,
                "data_point": {
                    "value": int('{:x}{:02x}'.format(to_int(data[30]), to_int(data[29])), 16) / 10.0,
                    "timestamp": timestamp
                }
            }
        )
    if 'pga' in allow_metrics:
        content['metrics'].append(
            {
                "name": "pga",
                "namespace": MACHINIST_NAMESPACE,
                "data_point": {
                    "value": int('{:x}{:02x}'.format(to_int(data[32]), to_int(data[31])), 16) / 10.0,
                    "timestamp": timestamp
                }
            }
        )
    if 'seismic_intensity' in allow_metrics:
        content['metrics'].append(
            {
                "name": "seismic_intensity",
                "namespace": MACHINIST_NAMESPACE,
                "data_point": {
                    "value": int('{:x}{:02x}'.format(to_int(data[34]), to_int(data[33])), 16) / 1000.0,
                    "timestamp": timestamp
                }
            }
        )

    send_data = json.dumps(content)
    req = urllib2.Request(MACHINIST_URL, data=send_data, headers=headers)
    res = urllib2.urlopen(req)
    body = res.read().decode("ascii")
    send_result = json.loads(body)
    send_result.update({ 'timestamp' : time_measured.strftime("%Y/%m/%d %H:%M:%S") })
    print(json.dumps(send_result, sort_keys=True, indent=4))

if __name__ == "__main__":
    ser = serial.Serial(SENSOR_SERIAL_DEVICE, 115200, serial.EIGHTBITS, serial.PARITY_NONE)

    try:
        command = bytearray([0x52, 0x42, 0x0a, 0x00, 0x02, 0x11, 0x51, SENSOR_NORMALLY_ON, 0x00, 0, 255, 0])
        command = command + calc_crc(command, len(command))
        ser.write(command)
        time.sleep(0.1)
        ret = ser.read(ser.inWaiting())
        while ser.isOpen():
            command = bytearray([0x52, 0x42, 0x05, 0x00, 0x01, 0x21, 0x50])
            command = command + calc_crc(command, len(command))
            tmp = ser.write(command)
            time.sleep(0.1)
            data = ser.read(ser.inWaiting())
            now = datetime.datetime.now()
            if len(data) != SENSOR_VALID_DATALEN:
                print(json.dumps({ 'message': 'Invalid data length', 'timestamp': now.strftime("%Y/%m/%d %H:%M:%S"), 'errors': [ { 'detail': len(data) } ] }))
                continue
            send_machinist(data, time_measured=now)
            time.sleep(60)
    except:
        traceback.print_exc()
        command = bytearray([0x52, 0x42, 0x0a, 0x00, 0x02, 0x11, 0x51, SENSOR_NORMALLY_OFF, 0x00, 0, 0, 0])
        command = command + calc_crc(command, len(command))
        ser.write(command)
        time.sleep(1)
        sys.exit(1)
    sys.exit(0)
