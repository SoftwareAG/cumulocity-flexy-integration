"""Provide core functionality in blueprints such as easy access to the logger
"""
import logging
from werkzeug.local import LocalProxy
from flask import current_app

logger: logging.Logger = LocalProxy(lambda: current_app.logger)
