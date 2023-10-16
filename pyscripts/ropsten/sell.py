# ---------------------------------------------
# SELL.PY -------------------------------------
# ---------------------------------------------
# Sell an amount of team tokens,
# with logging, passing args via cmd line
#
# usage: sell.py [-h] team amount
#
# positional arguments:
#   team      team name where you want to sell
#             token [TEAMF, TEAMM]
#   amount    amount of token you want to sell
#
# optional arguments:
#   -h, --help  show this help message and exit
#
# ---------------------------------------------
# ---------------------------------------------

from brownie import network, project
from solb.util import connect_network, load_act_from_prv_key
from solb.iod import reload_all_Contract
from solb.mng import sell
import argparse

if __name__ == '__main__':

    # utility for argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "team", help="team name where you want to sell token [TEAMF, TEAMM]")
    parser.add_argument("amount", help="amount of token you want to sell")
    args = parser.parse_args()

    # check/connect network states
    connect_network()

    # load brownie project
    prj = project.load()

    # load local AMPM account
    act = load_act_from_prv_key("AMPM-ORG")

    # Reload contracts with AMPM-ORG account as owner
    cnt_dict = reload_all_Contract(act)

    # Sell an amount of team tokens
    sell(cnt_dict, args.team.upper(), float(args.amount))

    # close project
    prj.close()

    # kill rpc local connection
    network.disconnect()
