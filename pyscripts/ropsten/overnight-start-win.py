# --------------------------------------------------------
# OVERNIGHT-START-WIN.PY ---------------------------------
# --------------------------------------------------------
# Start an overnight challenge, and try
# to automatically win it after the correct
# period of time, maybe increasing gasPrice
# With logging, passing args via cmd line
#
# usage: overnight-start-win.py [-h] percentage multiplier
#
# positional arguments:
#   percentage  percentage of price variation,
#               [-10,10] limits
#   multiplier  gasprice multiplier, default 1
#
# optional arguments:
#   -h, --help  show this help message and exit
#
# --------------------------------------------------------
# --------------------------------------------------------

from brownie import network, project
from solb.util import connect_network, load_act_from_prv_key
from solb.iod import reload_all_Contract
from solb.mng import overnight_start_win
import argparse

if __name__ == '__main__':

    # utility for argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("percentage",
                        help="percentage of price variation, [-10,10] limits")
    parser.add_argument("multiplier",
                        help="gasprice multiplier, default 1")
    args = parser.parse_args()

    # check/connect network states
    connect_network()

    # load brownie project
    prj = project.load()

    # load local AMPM account
    act = load_act_from_prv_key("AMPM-ORG")

    # Reload contracts with AMPM-ORG account as owner
    cnt_dict = reload_all_Contract(act)

    # Start an overnight challenge, and try to win it
    overnight_start_win(cnt_dict,
                        int(args.percentage),
                        int(args.multiplier))

    # close project
    prj.close()

    # kill rpc local connection
    network.disconnect()
