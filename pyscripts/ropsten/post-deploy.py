# ---------------------------------------------
# POST-DEPLOY.PY ------------------------------
# ---------------------------------------------
# Post deploy automatization for others team
# ---------------------------------------------
# ---------------------------------------------

from solb import iod
from solb.util import connect_network, create_cnt_dict
from brownie import network, accounts, project

if __name__ == '__main__':

    # check/connect network states
    connect_network()

    # load brownie project
    prj = project.load()

    # load local super user account
    act = accounts.load("referee")

    # load contract dict template
    cnt_dict = create_cnt_dict()

    # load payCoin token
    cnt_dict['payCoin'] = iod.load_payCoin()

    # load Lender
    cnt_dict['Lender'] = iod.load_Lender()

    # payCoin add challenge, exchange contracts of teams
    # as minters + burners, and also Lender
    iod.add_mb_payCoin(act, cnt_dict['payCoin'],
                       ['AMPM-ORG', 'TEAMF', 'TEAMM'])

    # payCoin mint 50k PaC to teams
    iod.refill_teams(act, cnt_dict['payCoin'],
                     ['AMPM-ORG', 'TEAMF', 'TEAMM'])

    # Lender add all teams as customers
    iod.add_cst_Lender(act, cnt_dict['Lender'],
                       ['AMPM-ORG', 'TEAMF', 'TEAMM'])

    # Set MB other teams referee and master referee
    refs = []
    iod.add_mb_referee(act, cnt_dict['payCoin'], refs)

    # close project
    prj.close()

    # kill rpc local connection
    network.disconnect()
