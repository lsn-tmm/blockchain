# --------------------------------------------
# UTIL.PY ------------------------------------
# --------------------------------------------
# General/Pre-deploy utilities ---------------
# --------------------------------------------
# --------------------------------------------

import os
import sys
import json
import logging
from decimal import Decimal
from brownie import network
from brownie import accounts
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from base64 import b64decode


class cc:
    B = '\033[94m'
    G = '\033[92m'
    Y = '\033[93m'
    R = '\033[91m'
    EC = '\033[0m'
    BOLD = '\033[1m'


def get_network_name():
    return os.path.relpath(__file__).split('/')[1]


def connect_network(local=False):
    net_name = get_network_name()
    try:
        if not(network.is_connected()):
            network.connect(net_name, launch_rpc=local)
        else:
            if network.show_active() != net_name:
                sprint("E: Wrong network active!", err=True)
                network.disconnect()
                eprint()
                sys.exit(1)
    except ConnectionError as cerr:
        sprint("E: Connection error!", err=True)
        print(str(cerr), file=sys.stderr)
        eprint()
        sys.exit(1)


def load_act_from_prv_key(name):
    """
    load local brownie account from encrypted private key,
    using $PAXBRONWIE shell variable to decrypt it
    """
    sprint(f"I: Import {name} account")
    try:
        print("Loading ... ", end='')
        home = os.getenv("HOME")
        passwd = os.getenv("PAXBROWNIE")
        with open(os.path.join(home, f".brownie/accounts/{name}.pycrypto"),
                  'r') as fs:
            cipher_json = json.load(fs)
        salt = b64decode(cipher_json['salt'].encode('utf-8'))
        iv = b64decode(cipher_json['iv'].encode('utf-8'))
        ciphered_text = b64decode(cipher_json['ciphertext'].encode('utf-8'))
        master_key = PBKDF2(passwd, salt, dkLen=32)
        cipher = AES.new(master_key, AES.MODE_CFB, iv=iv)
        prv_key = cipher.decrypt(ciphered_text)
        prv_key = prv_key.decode('utf-8')
        act = accounts.add(prv_key)
        print("ok")
        eprint()
        return act
    except Exception as cerr:
        print("errors")
        print("Check if file exits and/or $PAXBROWNIE is correct")
        print("Traceback")
        print(str(cerr), file=sys.stderr)
        eprint()
        sys.exit(1)


def sprint(msg, err=False):
    """wrapper around print"""
    print(cc.G +
          "------------------------------ STR ------------------------------"
          + cc.EC)
    print(msg, file=sys.stderr) if err else print(
        cc.BOLD+msg+cc.EC, file=sys.stdout)
    print("-----------------------------------------------------------------")


def eprint():
    """wrapper around print"""
    print(cc.R +
          "------------------------------ END ------------------------------"
          + cc.EC, end='\n\n')


def sci(num):
    """return scientific notation string of number"""
    return f"{Decimal(str(num)):.5E}" if num != 0 else 0


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


def create_cnt_dict():
    """create a empty contract dict to use as template"""
    tmp_dict = {'payCoin': None, 'Lender': None, 'AMPM-ORG': None,
                'TEAMF': None, 'TEAMM': None}
    for name in tmp_dict.keys():
        if name in ['payCoin', 'Lender']:
            None
        else:
            tmp_dict[name] = {'token': None,
                              'exchange': None, 'challenge': None}
    return tmp_dict
