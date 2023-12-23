FROM python:3-slim
WORKDIR /tmp
RUN pip install pyserial prometheus-client
COPY main.py /tmp/main.py
COPY sensor.py /tmp/sensor.py
ENTRYPOINT ["python3", "-u"]
CMD ["/tmp/main.py"]
