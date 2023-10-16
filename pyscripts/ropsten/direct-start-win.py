# --------------------------------------------------------
# DIRECT-START-WIN.PY ------------------------------------
# --------------------------------------------------------
# Start an direct challenge, and try
# to automatically win it after the correct
# period of time, maybe increasing gasPrice
# With logging, passing args via cmd line
#
# usage: direct-start-win.py [-h] team multiplier
#
# positional arguments:
#   team        team name you want to challenge
#               [TEAMF, TEAMM]
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
from solb.mng import direct_start_win
import argparse

if __name__ == '__main__':

    # utility for argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("team",
                        help="team name you want to challenge [TEAMF, TEAMM]")
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

    # Start a direct challenge, and try to win it
    direct_start_win(cnt_dict,
                     args.team.upper(),
                     int(args.multiplier))

    # close project
    prj.close()

    # kill rpc local connection
    network.disconnect()
