#!/usr/bin/env python3
from sensor import Sensor, SensorSerialError
from prometheus_client import start_http_server, Gauge
import time
import os, signal
import logging
logging.basicConfig(level=logging.DEBUG)

SENSOR_SERIAL_DEVICE = os.environ.get('SENSOR_SERIAL_DEVICE', '/dev/ttyUSB0')
SERVER_HTTP_PORT = int(os.environ.get('SERVER_HTTP_PORT', 8000))
start_http_server(SERVER_HTTP_PORT)
gauge = {
    'temperature': Gauge('sensor_omron_temperature', 'Temperature'),
    'relative_humidity': Gauge('sensor_omron_humidity', 'Humidity'),
    'ambient_light': Gauge('sensor_omron_light', 'Ambient light'),
    'barometric_pressure': Gauge('sensor_omron_barometric', 'Barometric pressure'),
    'sound_noise': Gauge('sensor_omron_noise', 'Sound noise'),
    'eTVOC': Gauge('sensor_omron_etvoc', 'eTVOC'),
    'eCO2': Gauge('sensor_omron_eco2', 'eCO2'),
    'discomfort_index': Gauge('sensor_omron_discomfort', 'Discomfort index'),
    'heat_stroke': Gauge('sensor_omron_heat', 'Heat stroke'),
    'vibration_information': Gauge('sensor_omron_vibration', 'Vibration information'),
    'si_value': Gauge('sensor_omron_si', 'SI value'),
    'pga': Gauge('sensor_omron_pga', 'PGA'),
    'seismic_intensity': Gauge('sensor_omron_seismic', 'Seismic intensity')
}

if __name__ == "__main__":
    logging.debug('start')
    sen = Sensor(SENSOR_SERIAL_DEVICE)
    signal.signal(signal.SIGTERM, lambda *args: sen.close())
    signal.signal(signal.SIGINT, lambda *args: sen.close())
    sen.open()
    try:
        while sen.isopen():
            try:
                for (k,v) in sen.read().get_all().items():
                    if k in gauge:
                        gauge[k].set(v)
            except SensorSerialError:
                logging.error('Sensor serial error occurred.', exc_info=True)
                time.sleep(10)
                continue
            time.sleep(60)
    except KeyboardInterrupt:
        pass
    except:
        logging.error('An error occurred.', exc_info=True)
    sen.close()
    logging.debug('end')
