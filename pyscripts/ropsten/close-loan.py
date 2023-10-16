# -----------------------------------------------
# CLOSE-LOAN.PY ---------------------------------
# -----------------------------------------------
# Close a loan with given id,
# with logging, passing args via cmd line
#
# usage: close-loan.py [-h] id
#
# positional arguments:
#   id          id of loan you want to close
#
# optional arguments:
#   -h, --help  show this help message and exit
#
# ------------------------------------------------
# ------------------------------------------------

from brownie import network, project
from solb.util import connect_network, load_act_from_prv_key
from solb.iod import reload_all_Contract
from solb.mng import loan_close
import argparse


if __name__ == '__main__':

    # utility for argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("id", help="id of loan you want to close")
    args = parser.parse_args()

    # check/connect network states
    connect_network()

    # load brownie project
    prj = project.load()

    # load local AMPM account
    act = load_act_from_prv_key("AMPM-ORG")

    # Reload contracts with AMPM-ORG account as owner
    cnt_dict = reload_all_Contract(act)

    # Close a loan with given id
    loan_close(cnt_dict, int(args.id))

    # close project
    prj.close()

    # kill rpc local connection
    network.disconnect()
