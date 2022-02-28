import threading
import schedule
import time
from ewon_flexy_integration.blueprints.datasynchronization import execute_all_jobs
from flask import Blueprint

bp = Blueprint('job_execution_schedule', __name__)

def run_continuously(interval=1):
    """Continuously run, while executing pending jobs at each
    elapsed time interval.
    @return cease_continuous_run: threading. Event which can
    be set to cease continuous run.
    """
    cease_continuous_run = threading.Event()

    class ScheduleThread(threading.Thread):
        """Responsible for periodically executing jobs

        Args:
            threading (_type_): _description_
        """
        @classmethod
        def run(cls):
            """Runs the scheduled job execution
            """
            while not cease_continuous_run.is_set():
                schedule.run_pending()
                time.sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.start()
    return cease_continuous_run

schedule.every().hour.do(execute_all_jobs)

# Start the background thread
run_continuously()