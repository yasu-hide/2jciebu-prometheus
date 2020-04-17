#!/usr/bin/env python
from sensor import Sensor, SensorSerialError
from machinist import Machinist, MachinistHTTPError
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
    
    for m_name in allow_metrics:
        metrics = {
            "name": m_name,
            "data_point": {}
        }
        if m_namespace:
            metrics['namespace'] = m_namespace
        if m_tags:
            metrics['tags'] = m_tags
        sen_name = "get_{}".format(m_name)
        if hasattr(sen, sen_name):
            metrics["data_point"]["value"] = getattr(sen, sen_name)()
        if timestamp:
            metrics['data_point']['timestamp'] = timestamp
        content['metrics'].append(metrics)
    return content

if __name__ == "__main__":
    logging.debug('start')
    m = Machinist(MACHINIST_APIKEY)
    sen = Sensor(SENSOR_SERIAL_DEVICE)
    signal.signal(signal.SIGTERM, lambda *args: sen.close())
    signal.signal(signal.SIGINT, lambda *args: sen.close())
    sen.open()
    try:
        while sen.isopen():
            now = datetime.datetime.now()
            try:
                metrics = metrics_data(sen, measured_at=now)
            except SensorSerialError:
                logging.error('Sensor serial error occurred.', exc_info=True)
                time.sleep(10)
                continue
            try:
                set_result = m.set_latest(metrics)
                sys.stderr.write(json.dumps(set_result, sort_keys=True, indent=4) + "\n")
            except MachinistHTTPError:
                logging.error('Machinist http error occurred.', exc_info=True)
            time.sleep(60)
    except KeyboardInterrupt:
        pass
    except:
        logging.error('An error occurred.', exc_info=True)
    sen.close()
    logging.debug('end')
