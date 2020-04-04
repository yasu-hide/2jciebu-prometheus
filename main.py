#!/usr/bin/env python
from sensor import Sensor
from machinist import Machinist
import json
import sys, os, time
import threading, logging
if sys.version_info.major != 2:
    from queue import Queue
else:
    from Queue import Queue
logging.basicConfig(level=logging.DEBUG, format='%(threadName)s: %(message)s')

SENSOR_SERIAL_DEVICE = os.environ.get('SENSOR_SERIAL_DEVICE', '/dev/ttyUSB0')
MACHINIST_APIKEY = os.environ.get('MACHINIST_APIKEY', '')

def sensor_metrics(data, agent='env_sensor'):
    m_namespace = os.environ.get('MACHINIST_NAMESPACE', agent)
    allow_metrics = os.environ.get('MACHINIST_SEND_METRICS', '').split()
    to_int = lambda s: int(s.encode('hex'), 16)
    content = {
        "agent": agent,
        "metrics": []
    }

    if len(allow_metrics) < 1:
        return content

    if 'temperature' in allow_metrics:
        content['metrics'].append(
            {
                "name": "temperature",
                "namespace": m_namespace,
                "data_point": {
                    "value": int('{:x}{:02x}'.format(to_int(data[9]), to_int(data[8])), 16) / 100.0,
                }
            }
        )
    if 'relative_humidity' in allow_metrics:
        content['metrics'].append(
            {
                "name": "relative_humidity",
                "namespace": m_namespace,
                "data_point": {
                    "value": int('{:x}{:02x}'.format(to_int(data[11]), to_int(data[10])), 16) / 100.0,
                }
            }
        )
    if 'ambient_light' in allow_metrics:
        content['metrics'].append(
            {
                "name": "ambient_light",
                "namespace": m_namespace,
                "data_point": {
                    "value": int('{:x}{:02x}'.format(to_int(data[13]), to_int(data[12])), 16),
                }
            }
        )
    if 'barometric_pressure' in allow_metrics:
        content['metrics'].append(
            {
                "name": "barometric_pressure",
                "namespace": m_namespace,
                "data_point": {
                    "value": int('{:x}{:02x}{:02x}{:02x}'.format(to_int(data[17]), to_int(data[16]), to_int(data[15]), to_int(data[14])), 16) / 1000.0,
                }
            }
        )
    if 'sound_noise' in allow_metrics:
        content['metrics'].append(
            {
                "name": "sound_noise",
                "namespace": m_namespace,
                "data_point": {
                    "value": int('{:x}{:02x}'.format(to_int(data[19]), to_int(data[18])), 16) / 100.0,
                }
            }
        )
    if 'eTVOC' in allow_metrics:
        content['metrics'].append(
            {
                "name": "eTVOC",
                "namespace": m_namespace,
                "data_point": {
                    "value": int('{:x}{:02x}'.format(to_int(data[21]), to_int(data[20])), 16),
                }
            }
        )
    if 'eCO2' in allow_metrics:
        content['metrics'].append(
            {
                "name": "eCO2",
                "namespace": m_namespace,
                "data_point": {
                    "value": int('{:x}{:02x}'.format(to_int(data[23]), to_int(data[22])), 16),
                }
            }
        )
    if 'discomfort_index' in allow_metrics:
        content['metrics'].append(
            {
                "name": "discomfort_index",
                "namespace": m_namespace,
                "data_point": {
                    "value": int('{:x}{:02x}'.format(to_int(data[25]), to_int(data[24])), 16) / 100.0,
                }
            }
        )
    if 'heat_stroke' in allow_metrics:
        content['metrics'].append(
            {
                "name": "heat_stroke",
                "namespace": m_namespace,
                "data_point": {
                    "value": int('{:x}{:02x}'.format(to_int(data[27]), to_int(data[26])), 16) / 100.0,
                }
            }
        )
    if 'vibration_information' in allow_metrics:
        content['metrics'].append(
            {
                "name": "vibration_information",
                "namespace": m_namespace,
                "data_point": {
                    "value": int('{:x}'.format(to_int(data[28])), 16),
                }
            }
        )
    if 'si_value' in allow_metrics:
        content['metrics'].append(
            {
                "name": "si_value",
                "namespace": m_namespace,
                "data_point": {
                    "value": int('{:x}{:02x}'.format(to_int(data[30]), to_int(data[29])), 16) / 10.0,
                }
            }
        )
    if 'pga' in allow_metrics:
        content['metrics'].append(
            {
                "name": "pga",
                "namespace": m_namespace,
                "data_point": {
                    "value": int('{:x}{:02x}'.format(to_int(data[32]), to_int(data[31])), 16) / 10.0,
                }
            }
        )
    if 'seismic_intensity' in allow_metrics:
        content['metrics'].append(
            {
                "name": "seismic_intensity",
                "namespace": m_namespace,
                "data_point": {
                    "value": int('{:x}{:02x}'.format(to_int(data[34]), to_int(data[33])), 16) / 1000.0,
                }
            }
        )
    return content

def sensor_worker(th_queue):
    logging.debug('start')
    sen = Sensor(SENSOR_SERIAL_DEVICE)
    sen.open()
    try:
        while sen.isopen():
            data = sen.read()
            metrics = sensor_metrics(data)
            th_queue.put(metrics)
            time.sleep(60)
    except:
        sen.close()
    logging.debug('end')

if __name__ == "__main__":
    logging.debug('start')
    m = Machinist(MACHINIST_APIKEY)
    th_queue = Queue()

    sens_th = threading.Thread(name='SensorThread', target=sensor_worker, args=(th_queue,))

    sens_th.start()

    while True:
        metrics = th_queue.get()
        result = m.set_latest(metrics)
        logging.info(json.dumps(result, sort_keys=True, indent=4))

    sens_th.join()

    logging.debug('end')
