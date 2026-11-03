import logging
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

def get_logger():
    logger = logging.getLogger("TaskAutomation")
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler(
            LOG_DIR / "task_automation.log",
            encoding="utf-8"
        )
        handler.setFormatter(logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s"
        ))
        logger.addHandler(handler)
    return logger
