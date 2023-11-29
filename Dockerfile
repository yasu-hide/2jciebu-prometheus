FROM python:3.13.0a2-slim
WORKDIR /tmp
RUN pip install pyserial
COPY main.py /tmp/main.py
COPY sensor.py /tmp/sensor.py
COPY machinist.py /tmp/machinist.py
ENTRYPOINT ["python", "-u"]
CMD ["/tmp/main.py"]
