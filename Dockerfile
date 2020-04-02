FROM python:2-slim-stretch
WORKDIR /tmp
RUN pip install pyserial
COPY main.py /tmp/main.py
ENTRYPOINT ["python", "-u"]
CMD ["/tmp/main.py"]
