# ---------------------------------------------
# PRE-DEPLOY.PY -------------------------------
# ---------------------------------------------
# Deploy PayCoin and Lender as referee
# (Pre deploy, cause before our/other cnts
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

    # deploy payCoin
    cnt_dict['payCoin'] = iod.deploy_payCoin(
        act, prj.GERC20)

    # deploy Lender
    cnt_dict['Lender'] = iod.deploy_Lender(
        act, prj.Lender, cnt_dict['payCoin'])

    # close project
    prj.close()

    # kill rpc local connection
    network.disconnect()
