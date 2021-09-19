#!/usr/bin/env python
from sensor import Sensor, SensorSerialError
from machinist import Machinist, MachinistHTTPError
from nanohat_oled import NanoHatOled
import json, time, datetime
import sys, os, signal
import traceback, logging
logging.basicConfig(level=logging.DEBUG)

SENSOR_SERIAL_DEVICE = os.environ.get('SENSOR_SERIAL_DEVICE', '/dev/ttyUSB0')
MACHINIST_APIKEY = os.environ.get('MACHINIST_APIKEY', '')

def metrics_data(sen, measured_at=datetime.datetime.now()):
    m_agent = os.environ.get('MACHINIST_AGENT', None)
    m_agent_id = os.environ.get('MACHINIST_AGENT_ID', None)
    m_namespace = os.environ.get('MACHINIST_NAMESPACE', None)
    tag_set = os.environ.get('MACHINIST_TAGS', '').split()
    allow_metrics = os.environ.get('MACHINIST_SEND_METRICS', '').split()
    timestamp = int(time.mktime(measured_at.timetuple()))

    content = {
        "metrics": []
    }
    if m_agent:
        content['agent'] = m_agent
    elif m_agent_id:
        content['agent_id'] = m_agent_id
    else:
        raise ValueError("Environment variable MACHINIST_AGENT or MACHINIST_AGENT_ID is required.")

    m_tags = {}
    for tg in tag_set:
        tag_name, tag_value = tg.split(':', 1)
        if tag_name and tag_value:
            tag_name = tag_name.strip()
            tag_value = tag_value.strip()
            if tag_name in m_tags:
                logging.warn("duplicate key in MACHINIST_TAGS: {}".format(tag_name))
            m_tags[tag_name] = tag_value            

    if len(allow_metrics) < 1:
        return content
    sen_data = sen.read().get_all()
    for m_name in allow_metrics:
        metrics = {
            "name": m_name,
            "data_point": {}
        }
        if m_namespace:
            metrics['namespace'] = m_namespace
        if m_tags:
            metrics['tags'] = m_tags
        if m_name in sen_data:
            metrics["data_point"]["value"] = sen_data[m_name]
        else:
            logging.warn("no key in sensor data: {}".format(m_name))
            continue
        if timestamp:
            metrics['data_point']['timestamp'] = timestamp
        content['metrics'].append(metrics)
    return content

if __name__ == "__main__":
    logging.debug('start')
    m = Machinist(MACHINIST_APIKEY)
    sen = Sensor(SENSOR_SERIAL_DEVICE)
    oled = None
    try:
        oled = NanoHatOled()
        oled.start()
    except:
        oled = None
    signal.signal(signal.SIGTERM, lambda *args: sen.close())
    signal.signal(signal.SIGINT, lambda *args: sen.close())
    sen.open()
    lastrun_date = datetime.datetime.fromtimestamp(0)
    try:
        while sen.isopen():
            now = datetime.datetime.now()
            try:
                metrics = metrics_data(sen, measured_at=now)
            except SensorSerialError:
                logging.error('Sensor serial error occurred.', exc_info=True)
                time.sleep(10)
                continue
            if oled:
                oled.put_image(sen.get_temperature(), sen.get_relative_humidity(), sen.get_eCO2(), sen.get_barometric_pressure())
                oled.queue.join()
            if now >= lastrun_date + datetime.timedelta(seconds=60):
                try:
                    set_result = m.set_latest(metrics)
                    sys.stderr.write(json.dumps({ "date": str(now), "result": set_result}, sort_keys=True, indent=4) + "\n")
                except MachinistHTTPError:
                    logging.error('Machinist http error occurred.', exc_info=True)
                lastrun_date = now
            time.sleep(3)
    except:
        logging.error('An error occurred.', exc_info=True)
    finally:
        if oled:
            oled.oled_close()
        sen.close()
    logging.debug('end')
