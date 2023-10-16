# --------------------------------------------
# MAIN.PY ------------------------------------
# --------------------------------------------
# Simulation of main-challenge, using copies
# of our contracts deployed with fake acts
# --------------------------------------------
# --------------------------------------------

from brownie import network, accounts, project
from solb.util import connect_network, create_cnt_dict
from solb import iod
from solb import mng
# from multiprocessing import Process

if __name__ == '__main__':

    # check/connect network states
    connect_network(local=True)

    # load brownie project
    prj = project.load()

    try:

        # *********************************
        # DEPLOY **************************
        # *********************************
        # *********************************

        input("START DEPLOY [Enter] ")

        # [ONLY IN DEV] setup fake accounts
        act_dict = {}
        act_dict['referee'] = accounts[-1]
        act_dict['AMPM-ORG'] = accounts[0]
        act_dict['TEAMF'] = accounts[1]
        act_dict['TEAMM'] = accounts[2]
        iod.dump_team_address(act_dict)

        # load contract dict template
        cnt_dict = create_cnt_dict()

        # [ONLY IN DEV] deploy fake payCoin
        cnt_dict['payCoin'] = iod.deploy_payCoin(
            act_dict['referee'], prj.GERC20)

        # [ONLY IN DEV] deploy fake Lender
        cnt_dict['Lender'] = iod.deploy_Lender(
            act_dict['referee'], prj.Lender, cnt_dict['payCoin'])

        # load payCoin token (only to simulate from_abi)
        cnt_dict['payCoin'] = iod.load_payCoin()

        # deploy AMPM token
        cnt_dict['AMPM-ORG']['token'] = iod.deploy_AMPM(
            act_dict['AMPM-ORG'], prj.AMPM)

        # deploy AMPM exchange
        cnt_dict['AMPM-ORG']['exchange'] = iod.deploy_ExchangeAMPM(
            act_dict['AMPM-ORG'], prj.ExchangeAMPM, cnt_dict['payCoin'],
            cnt_dict['AMPM-ORG']['token'])

        # deploy AMPM challenge
        cnt_dict['AMPM-ORG']['challenge'] = iod.deploy_ChallengeAMPM(
           act_dict['AMPM-ORG'], prj.ChallengeAMPM, cnt_dict['payCoin'],
           cnt_dict['AMPM-ORG']['exchange'])

        # [ONLY IN DEV] deploy other team token
        for act in list(act_dict.keys())[2:]:
            cnt_dict[act]['token'] = iod.deploy_GERC20(
                act, act_dict[act], prj.GERC20)

        # [ONLY IN DEV] deploy other team exhange
        for act in list(act_dict.keys())[2:]:
            cnt_dict[act]['exchange'] = iod.deploy_Exchange(
                act, act_dict[act], prj.ExchangeAMPM,
                cnt_dict['payCoin'], cnt_dict[act]['token'])

        # [ONLY IN DEV] deploy other team challenge
        for act in list(act_dict.keys())[2:]:
            cnt_dict[act]['challenge'] = iod.deploy_Challenge(
                act, act_dict[act], prj.ChallengeAMPM,
                cnt_dict['payCoin'], cnt_dict[act]['exchange'])

        # *********************************
        # POST-DEPLOY *********************
        # *********************************
        # *********************************

        input("START POST-DEPLOY [Enter] ")

        # [ONLY IN DEV] payCoin mint 50k PaC to teams
        iod.refill_teams(act_dict['referee'], cnt_dict['payCoin'],
                         list(act_dict.keys())[1:])

        # [ONLY IN DEV] payCoin add challenge,
        # exchange contracts of teams and Lender as minters + burners
        iod.add_mb_payCoin(act_dict['referee'], cnt_dict['payCoin'],
                           list(act_dict.keys())[1:])

        # token AMPM add exchange contract as minter + burner
        iod.add_mb_AMPM(act_dict['AMPM-ORG'], cnt_dict['AMPM-ORG']['token'])

        # exchange AMPM add customers
        # challenge AMPM add customers
        iod.add_cst_AMPM(act_dict['AMPM-ORG'], cnt_dict['AMPM-ORG'])

        # exchange AMPM add challenge AMPM as manager
        iod.add_mng_AMPM(act_dict['AMPM-ORG'],
                         cnt_dict['AMPM-ORG']['exchange'])

        # [ONLY IN DEV] token other teams add exchange,
        # contract of relative team as minter + burner
        for act in list(act_dict.keys())[2:]:
            iod.add_mb_GERC20(act, act_dict[act], cnt_dict[act]['token'])

        # [ONLY IN DEV] other team exchange add AMPM as customer
        # [ONLY IN DEV] other team challenge add AMPM as customer
        for act in list(act_dict.keys())[2:]:
            iod.add_cst_cteam(act, act_dict[act], cnt_dict[act])

        # [ONLY IN DEV] exchange other team add challenge other team as manager
        for act in list(act_dict.keys())[2:]:
            iod.add_mng_cteam(act, act_dict[act], cnt_dict[act]['exchange'])

        # [ONLY IN DEV] Lender add all teams as customers
        iod.add_cst_Lender(act_dict['referee'], cnt_dict['Lender'],
                           list(act_dict.keys())[1:])

        # *********************************
        # POST-DEPLOY-CHECK ***************
        # *********************************
        # *********************************

        input("START POST-DEPLOY-CHECK [Enter] ")

        # Reload contracts (only for testing purpose) with
        # AMPM-ORG account as owner
        cnt_dict = iod.reload_all_Contract(act_dict['AMPM-ORG'])

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

        # Check if AMPM is customer of
        # other team Exchange and Challenge
        for name in cnt_dict.keys():
            if name in ['payCoin', 'Lender', 'AMPM-ORG']:
                None
            else:
                iod.check_cst_cteam(name, cnt_dict[name])

        # Check if AMPM is customer of Lender
        iod.check_cst_Lender(cnt_dict['Lender'])

        # *********************************
        # CHANGE PRICE ********************
        # *********************************
        # *********************************

        input("START CHANGE-PRICE [Enter] ")

        # Reload contracts (only for testing purpose) with
        # AMPM-ORG account as owner
        # cnt_dict = iod.reload_all_Contract(act_dict['AMPM-ORG'])

        # Start change price
        # mng.change_price(cnt_dict['AMPM-ORG']['exchange'])

        #
        # [IDEV]
        # CREATE A MULTIPROCESS TO PERMIT
        # EXECUTION OF NEXT FUNCTION
        #
        # pc = Process(name="changePrice",
        #              target=mng.change_price,
        #              args=(cnt_dict['AMPM-ORG']['exchange'], ))
        #
        # pc.start()
        #
        # PLACE THIS BLOCK AFTER FUNCTION
        # YOU WANT TO RUN AFTER CHANGE PRICE
        #
        # try:
        #     pc.join()
        # except KeyboardInterrupt:
        #     pc.terminate()
        #

        # *********************************
        # BUY/SELL INTERACTION ************
        # *********************************
        # *********************************

        input("START BUY/SELL [Enter] ")

        # Reload contracts (only for testing purpose) with
        # AMPM-ORG account as owner
        cnt_dict = iod.reload_all_Contract(act_dict['AMPM-ORG'])

        # [IDEV] Change starting date of TEAMF team exchange
        mng.change_start_to_now(cnt_dict['TEAMF']['exchange'],
                                act_dict['TEAMF'])

        # Print balances
        mng.balance_digest(cnt_dict, 'TEAMF')

        # Print balances
        mng.balance_digest(cnt_dict, 'AMPM-ORG', act_dict['AMPM-ORG'])

        # Buy token of TEAMF team
        mng.buy(cnt_dict, 'TEAMF', 1)

        # Print balances
        mng.balance_digest(cnt_dict, 'TEAMF')

        # Print balances
        mng.balance_digest(cnt_dict, 'AMPM-ORG', act_dict['AMPM-ORG'])

        # Sell token of TEAMF team
        mng.sell(cnt_dict, 'TEAMF', 1)

        # Print balances
        mng.balance_digest(cnt_dict, 'TEAMF')

        # Print balances
        mng.balance_digest(cnt_dict, 'AMPM-ORG', act_dict['AMPM-ORG'])

        # *********************************
        # CHALLENGE INTERACTION ***********
        # *********************************
        # *********************************

        input("START CHALLENGES [Enter] ")

        # Reload contracts (only for testing purpose) with
        # AMPM-ORG account as owner
        cnt_dict = iod.reload_all_Contract(act_dict['AMPM-ORG'])

        # Start Direct Challenge as AMPM-ORG vs TEAMF
        mng.direct_challenge_start(cnt_dict, 'TEAMF')

        # Try to win Direct Challenge as AMPM-ORG vs TEAMF
        mng.direct_check(cnt_dict, 'AMPM-ORG', 0)

        # Start Team Challenge as AMPM-ORG vs other teams
        mng.team_challenge_start(cnt_dict)

        # Try to win Team Challenge as AMPM-ORG vs other teams
        mng.team_check(cnt_dict, 'AMPM-ORG', 0)

        # Start Overnight Challenge as AMPM-ORG
        mng.overnight_start(cnt_dict, -10)

        # Try to win Overnight Challenge as AMPM-ORG
        mng.overnight_check(cnt_dict, 'AMPM-ORG', 1)

        # *********************************
        # OPEN/CLOSE LOAN *****************
        # *********************************
        # *********************************

        input("START OPEN/CLOSE LOAN [Enter] ")

        # Reload contracts (only for testing purpose) with
        # AMPM-ORG account as owner
        cnt_dict = iod.reload_all_Contract(act_dict['AMPM-ORG'])

        # Open a Loan to Lender
        id = mng.loan_open(cnt_dict['Lender'], 1)

        # Close a Loan to Lender
        mng.loan_close(cnt_dict, id)

        # *********************************
        # NEW CHAPTER *********************
        # *********************************
        # *********************************

        # [ONLY IN DEV] flush addresses and abis
        # (to obtain empty json template)
        iod.flush_addresses_abis()

        # close project
        prj.close()

        # kill rpc local connection
        network.disconnect(kill_rpc=True) if network.is_connected() else None

    except (Exception, KeyboardInterrupt):

        # [ONLY IN DEV] flush addresses and abis
        # (to obtain empty json template)
        iod.flush_addresses_abis()

        # close project
        prj.close()

        # kill rpc local connection
        network.disconnect(kill_rpc=True) if network.is_connected() else None
