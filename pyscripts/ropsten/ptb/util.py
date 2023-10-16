# --------------------------------------------
# UTIL.PY ------------------------------------
# --------------------------------------------
# Utilities func for py TG bot ---------------
# --------------------------------------------
# --------------------------------------------

import os
import sys
import logging


def getpybotTKN():
    """get Telegram bot TKN using shell var"""
    py_bot = os.getenv("PY_BOT_TOKEN")
    if py_bot is None:
        print("Export $PY_BOT_TOKEN shell variable", file=sys.stderr)
        sys.exit(1)
    else:
        return py_bot


def pybrownie():
    """get python brownie bin path using shell var"""
    py_brownie = os.getenv("PY_BROWNIE")
    if py_brownie is None:
        print("Export $PY_BROWNIE shell variable", file=sys.stderr)
        sys.exit(1)
    else:
        return py_brownie


def setup_logger(name, logfile):
    """setup logger"""
    handler = logging.FileHandler(logfile)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s',
                                  datefmt='%d-%b-%y %H:%M:%S')
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    return logger


def write_args(name, *args):
    """write args to EnvironmentFile for systemd <name>.service"""
    with open(f"pyscripts/ropsten/args/{name}.args", 'w') as fs:
        for i, arg in enumerate(args):
            fs.write(f'ARG{i+1}="{arg}"\n')
