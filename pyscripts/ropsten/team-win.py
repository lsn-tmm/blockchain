# --------------------------------------------------------
# TEAM-WIN.PY --------------------------------------------
# --------------------------------------------------------
# Try automatically team a direct after the correct
# period of time, maybe increasing gasPrice
# With logging, passing args via cmd line
#
# usage: team-win.py [-h] team flag dtime multiplier
#
# positional arguments:
#   team        team name you want to challenge [TEAMF, TEAMM]
#   flag        flag emitted
#   dtime       time to sleep, before try to win
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
from solb.mng import team_check
import time
import argparse

if __name__ == '__main__':

    # utility for argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("team",
                        help="team name you want to challenge [TEAMF, TEAMM]")
    parser.add_argument("flag",
                        help="flag emitted")
    parser.add_argument("dtime",
                        help="time to sleep, before try to win")
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

    # Win a team challenge
    time.sleep(int(args.dtime))
    team_check(cnt_dict,
               args.team.upper(),
               int(args.flag),
               mul=int(args.multiplier))

    # close project
    prj.close()

    # kill rpc local connection
    network.disconnect()
