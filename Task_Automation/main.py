from ui.app import launch
from core.logger import get_logger

if __name__ == "__main__":
    logger = get_logger()
    logger.info("Task Automation Pro started")

    try:
        launch()
    except Exception:
        logger.exception("Application crashed")
        raise
