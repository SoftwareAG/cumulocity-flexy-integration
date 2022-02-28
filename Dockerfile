FROM python:3.9-slim as production

# Install python dependencies
COPY requirements/requirements.txt /tmp
RUN pip3 install wheel \
    && pip3 install -r /tmp/requirements.txt

# Copy already built app
COPY build/lib/ewon_flexy_integration /app/ewon_flexy_integration

# Copy gunicorn server/config
COPY server.py config.py /app/
WORKDIR /app

ENV PYTHONPATH="/app:.:$PYTHONPATH"
ENV PROMETHEUS_MULTIPROC_DIR /tmp
ENV prometheus_multiproc_dir /tmp

CMD gunicorn -c config.py -w 4 -b 0.0.0.0:80 --workers=4 --threads=2 --timeout=400 --log-level=warning server:app