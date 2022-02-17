"""Production server to run the microservice using gunicorn
"""
import logging

from flask.logging import default_handler

from ewon_flexy_integration.main import create_app

app = create_app()
gunicorn_logger = logging.getLogger('gunicorn.error')
# app.logger.removeHandler(default_handler)  # use custom loggers instead
app.logger.setLevel(gunicorn_logger.level)
app.logger.handlers = gunicorn_logger.handlers

app.logger.warning(f'Log handles: {gunicorn_logger.handlers}')

if __name__ == '__main__':
    app.run(debug=False, port=5000)
