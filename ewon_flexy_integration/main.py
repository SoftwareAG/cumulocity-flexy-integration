"""Microservice application which configures the app and combines all of the handlers"""
import logging
import json

from flask import Flask
from werkzeug.exceptions import HTTPException
from prometheus_flask_exporter.multiprocess import GunicornInternalPrometheusMetrics

import ewon_flexy_integration
from ewon_flexy_integration.blueprints import datasynchronization, job_execution_schedule, version, agent_release
from ewon_flexy_integration.blueprints import health
from ewon_flexy_integration.blueprints import datamailbox
from ewon_flexy_integration.blueprints import loglevel

metrics = GunicornInternalPrometheusMetrics.for_app_factory()

logger = logging.getLogger('device certification')
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def create_app(config_filename=None) -> Flask:
    """Application factory function
    """
    app = Flask(__name__, instance_relative_config=True)
    if config_filename:
        app.config.from_pyfile(config_filename)

    register_blueprints(app)

    # static information as metric
    try:
        metrics.info('app_info', 'Application info',
                     version=ewon_flexy_integration.__version__)
    except ValueError:
        # NOTE: ignore Value error as metrics can only be registered once
        # otherwise a duplicate exception is raised. If a better way is
        # found, then it can be removed.
        pass
    metrics.init_app(app)

    return app


def register_blueprints(app: Flask):
    """Register blueprints
    """
    app.register_error_handler(HTTPException, handle_exception)

    app.register_blueprint(health.bp)
    app.register_blueprint(datamailbox.bp, url_prefix='/datamailbox')
    app.register_blueprint(version.bp)
    app.register_blueprint(loglevel.bp)
    app.register_blueprint(datasynchronization.bp)
    app.register_blueprint(job_execution_schedule.bp)
    app.register_blueprint(agent_release.bp)


def handle_exception(e: HTTPException):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "code": e.code,
        "error": e.name,
        "message": e.description,
    })
    response.content_type = "application/json"
    return response


if __name__ == '__main__':
    main_app = create_app()
    logging.debug('Generate cumulocity_flexy_integration app and listen to port 80')
    main_app.run(host='0.0.0.0', port=80, debug=True, threaded=False)
