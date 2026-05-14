import logging
import os
from datetime import datetime
from pathlib import Path


def get_logger(name: str, log_dir: str = "logs") -> logging.Logger:
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    log_file = os.path.join(
        log_dir,
        f"log_{datetime.utcnow().strftime('%Y_%m_%d')}.log"
    )
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        # File handler
        fh = logging.FileHandler(log_file, mode='a', encoding='utf-8')
        fh.setLevel(logging.INFO)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        logger.addHandler(fh)
        logger.addHandler(ch)
    
    return logger


def cleanup_old_logs(log_dir: str = "logs", retention_days: int = 7):
    import time
    now = time.time()
    for f in Path(log_dir).glob("*.log"):
        if (now - f.stat().st_ctime) // (24 * 3600) >= retention_days:
            f.unlink()