# ---------------------------------------------
# BALANCE-DIGEST.PY ---------------------------
# ---------------------------------------------
# Balances digest of a given team,
# passing args via cmd line
#
# usage: balance-digest.py [-h] team
#
# positional arguments:
#   team        team name you want to check
#               balances
#
# optional arguments:
#   -h, --help  show this help message and exit
#
# ---------------------------------------------
# ---------------------------------------------

from brownie import network, project
from solb.util import connect_network, load_act_from_prv_key
from solb.iod import reload_all_Contract
from solb.mng import balance_digest
import argparse

if __name__ == '__main__':

    # utility for argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "team", help="team name you want to check balances")
    args = parser.parse_args()

    # check/connect network states
    connect_network()

    # load brownie project
    prj = project.load()

    # load local AMPM account
    act = load_act_from_prv_key("AMPM-ORG")

    # Reload contracts with AMPM-ORG account as owner
    cnt_dict = reload_all_Contract(act)

    # Check balances of a team
    # (additional information about Wei if team is our)
    if args.team.upper() == 'AMPM-ORG':
        balance_digest(cnt_dict, args.team.upper(), act)
    else:
        balance_digest(cnt_dict, args.team.upper())

    # close project
    prj.close()

    # kill rpc local connection
    network.disconnect()
