# --------------------------------------------
# DEPLOY-CHECK.PY ----------------------------
# --------------------------------------------
# Check post-deploy automatization for what
# concern AMPM-ORG
# --------------------------------------------
# --------------------------------------------

from brownie import network, project
from solb.util import connect_network, load_act_from_prv_key
from solb import iod

if __name__ == '__main__':

    # check/connect network states
    connect_network()

    # load brownie project
    prj = project.load()

    # load local AMPM account
    act = load_act_from_prv_key("AMPM-ORG")

    # Reload contracts with AMPM-ORG account as owner
    cnt_dict = iod.reload_all_Contract(act)

    # Check balance in PaC of AMPM-ORG (and other teams)
    iod.check_PaC_balance(cnt_dict['payCoin'])

    # Check if ExchangeAMPM and ChallengeAMPM (not other team)
    # are minter, burner of PaC
    iod.check_mb_token(cnt_dict['payCoin'], 'PaC')

    # Check if ExchangeAMPM and ChallengeAMPM (not other team)
    # are minter, burner of MPM (only Exchange must be MB)
    iod.check_mb_token(cnt_dict['AMPM-ORG']['token'], 'MPM')

    # Check if Challenge AMPM is a manager of Exchange AMPM
    iod.check_mng_AMPM(cnt_dict['AMPM-ORG']['exchange'])

    # Check if other teams are customers of Exchange, Challenge AMPM
    iod.check_cst_AMPM(cnt_dict['AMPM-ORG'])

    # Check if AMPM is customer of Lender
    # (To comment if no our Lender is chosen)
    # iod.check_cst_Lender(cnt_dict['Lender'])

    # close project
    prj.close()

    # kill rpc local connection
    network.disconnect()
