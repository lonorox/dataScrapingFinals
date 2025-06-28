import logging
def log():
    logger = logging.getLogger("logger")
    file = logging.FileHandler('logs.log', mode='w')
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file.setFormatter(formatter)
    logger.addHandler(file)
    return logger
log = log()
