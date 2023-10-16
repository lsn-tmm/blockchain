# -----------------------------------------------
# OPEN-LOAN.PY ----------------------------------
# -----------------------------------------------
# Open a loan for amount of PaC,
# with logging, passing args via cmd line
#
# usage: open-loan.py [-h] amount
#
# positional arguments:
#   amount      amount of token you want to loan
#
# optional arguments:
#   -h, --help  show this help message and exit
#
# ------------------------------------------------
# ------------------------------------------------

from brownie import network, project
from solb.util import connect_network, load_act_from_prv_key
from solb.iod import reload_all_Contract
from solb.mng import loan_open
import argparse


if __name__ == '__main__':

    # utility for argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("amount", help="amount of token you want to loan")
    args = parser.parse_args()

    # check/connect network states
    connect_network()

    # load brownie project
    prj = project.load()

    # load local AMPM account
    act = load_act_from_prv_key("AMPM-ORG")

    # Reload contracts with AMPM-ORG account as owner
    cnt_dict = reload_all_Contract(act)

    # Open a loan for a amount of PaC
    loan_open(cnt_dict['Lender'], int(args.amount))

    # close project
    prj.close()

    # kill rpc local connection
    network.disconnect()
