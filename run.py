import subprocess
import sys
import time

from logging_config import get_logger


logger = get_logger(__name__)


def run_services():
    logger.info("application_starting")

    api_process = None
    streamlit_process = None

    try:
        logger.info(
            "backend_starting",
            extra={
                "details": {
                    "service": "fastapi",
                    "port": 8000
                }
            }
        )

        api_process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "api:app",
                "--reload",
                "--port",
                "8000"
            ]
        )

        time.sleep(2)

        logger.info(
            "backend_started",
            extra={
                "details": {
                    "service": "fastapi",
                    "pid": api_process.pid,
                    "port": 8000
                }
            }
        )

        logger.info(
            "frontend_starting",
            extra={
                "details": {
                    "service": "streamlit",
                    "port": 8501
                }
            }
        )

        streamlit_process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "streamlit",
                "run",
                "app.py"
            ]
        )

        logger.info(
            "frontend_started",
            extra={
                "details": {
                    "service": "streamlit",
                    "pid": streamlit_process.pid,
                    "port": 8501
                }
            }
        )

        logger.info("application_started")

        api_process.wait()
        streamlit_process.wait()

    except KeyboardInterrupt:

        logger.info("application_shutdown_requested")

    except Exception as e:

        logger.exception(
            "application_runtime_failed",
            extra={
                "details": {
                    "error": str(e)
                }
            }
        )

    finally:

        if (
            streamlit_process
            and streamlit_process.poll() is None
        ):
            logger.info(
                "frontend_stopping",
                extra={
                    "details": {
                        "pid": streamlit_process.pid
                    }
                }
            )

            streamlit_process.terminate()
            streamlit_process.wait()

        if (
            api_process
            and api_process.poll() is None
        ):
            logger.info(
                "backend_stopping",
                extra={
                    "details": {
                        "pid": api_process.pid
                    }
                }
            )

            api_process.terminate()
            api_process.wait()

        logger.info("application_stopped")


if __name__ == "__main__":
    run_services()