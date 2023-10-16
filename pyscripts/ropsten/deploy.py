# --------------------------------------------
# DEPLOY.PY ----------------------------------
# --------------------------------------------
# Deploy and post-deploy automatization for
# AMPM-ORG contracts
# --------------------------------------------
# --------------------------------------------

from solb import iod
from brownie import network, project
from solb.util import (connect_network,
                       load_act_from_prv_key,
                       create_cnt_dict)

if __name__ == '__main__':

    # check/connect network states
    connect_network()

    # load brownie project
    prj = project.load()

    # load local AMPM account
    act = load_act_from_prv_key("AMPM-ORG")

    # load contract dict template
    cnt_dict = create_cnt_dict()

    # load payCoin token
    cnt_dict['payCoin'] = iod.load_payCoin()

    # deploy AMPM token
    cnt_dict['AMPM-ORG']['token'] = iod.deploy_AMPM(act, prj.AMPM)

    # deploy AMPM exchange
    cnt_dict['AMPM-ORG']['exchange'] = iod.deploy_ExchangeAMPM(
        act, prj.ExchangeAMPM, cnt_dict['payCoin'],
        cnt_dict['AMPM-ORG']['token'])

    # deploy AMPM challenge
    cnt_dict['AMPM-ORG']['challenge'] = iod.deploy_ChallengeAMPM(
       act, prj.ChallengeAMPM, cnt_dict['payCoin'],
       cnt_dict['AMPM-ORG']['exchange'])

    # token AMPM add exchange contract as minter + burner
    iod.add_mb_AMPM(act, cnt_dict['AMPM-ORG']['token'])

    # exchange AMPM add customers
    # challenge AMPM add customers
    iod.add_cst_AMPM(act, cnt_dict['AMPM-ORG'])

    # exchange AMPM add challenge AMPM as manager
    iod.add_mng_AMPM(act, cnt_dict['AMPM-ORG']['exchange'])

    # close project
    prj.close()

    # kill rpc local connection
    network.disconnect()
