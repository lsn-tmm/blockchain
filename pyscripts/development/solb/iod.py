# --------------------------------------------
# IOD.PY -------------------------------------
# --------------------------------------------
# Input/Output deploy functions --------------
# --------------------------------------------
# --------------------------------------------

import json
import os
from brownie import Contract
from solb.util import (sprint, eprint, get_network_name,
                       create_cnt_dict, sci)


def load_addresses():
    """load address dictionary template"""
    with open(f"addresses/{get_network_name()}/addresses.json", 'r') as fs:
        add = json.load(fs)
    return add


def load_events():
    """load events dictionary template"""
    with open(f"events/{get_network_name()}/events.json", 'r') as fs:
        eve = json.load(fs)
    return eve


def dump_addresses(add):
    """dump address dictionary updated"""
    with open(f"addresses/{get_network_name()}/addresses.json", 'w') as fs:
        json.dump(add, fs, indent=3)


def load_contract_abi(name, team=''):
    """dump contract abi owned by team, named name"""
    if team == '':
        with open(f"abis/{get_network_name()}/{name}.json", 'r') as fs:
            abi = json.load(fs)
    else:
        with open(f"abis/{get_network_name()}/{team}/{name}.json", 'r') as fs:
            abi = json.load(fs)
    return abi


def dump_contract_abi(abi, name, team=''):
    """dump contract abi owned by team, named name"""
    if team == '':
        with open(f"abis/{get_network_name()}/{name}.json", 'w') as fs:
            json.dump(abi, fs, indent=3)
    else:
        with open(f"abis/{get_network_name()}/{team}/{name}.json", 'w') as fs:
            json.dump(abi, fs, indent=3)


def dump_team_address(acts):
    """save team addresses"""
    add = load_addresses()
    for act in acts.keys():
        if (act == 'referee'):
            add[act] = acts[act].address
        else:
            add[act]['address'] = acts[act].address
    dump_addresses(add)


def get_init_price():
    """get init price for exchange"""
    with open(f"pyscripts/{get_network_name()}/price.history", 'r') as fs:
        init_price = int(float(fs.readline()))
    return init_price


def deploy_payCoin(own, cnt):
    """
    - deploy fake payCoin account as refereee
    - save abi and address
    """
    sprint("IDEV: Deploy payCoin contract as referee")
    tkn = own.deploy(cnt, "payCoin", 'PaC')
    eprint()
    dump_contract_abi(tkn.abi, 'payCoin')
    add = load_addresses()
    add['payCoin'] = tkn.address
    dump_addresses(add)
    return tkn


def deploy_Lender(own, cnt, tkn_PaC):
    """
    - deploy fake Lender account as referee
    - save abi and address
    """
    sprint("IDEV: Deploy Lender contract as referee")
    tkn = own.deploy(cnt, tkn_PaC)
    eprint()
    dump_contract_abi(tkn.abi, 'Lender')
    add = load_addresses()
    add['Lender'] = tkn.address
    dump_addresses(add)
    return tkn


def deploy_GERC20(name, own, cnt):
    """
    - deploy fake other team ERC20 token
    - save abi and address
    """
    sprint(f"IDEV: Deploy {name} token as {name}")
    tkn = own.deploy(cnt, name, name[2:])
    eprint()
    dump_contract_abi(tkn.abi, 'token', name)
    add = load_addresses()
    add[name]['token'] = tkn.address
    dump_addresses(add)
    return tkn


def deploy_Exchange(name, own, cnt, tkn_PaC, tkn_team):
    """
    - deploy fake other team Exchange
    - save abi and address
    """
    add = load_addresses()
    sprint(f"IDEV: Deploy {name} Exchange as {name}")
    tkn = own.deploy(cnt, get_init_price(), tkn_PaC, tkn_team)
    eprint()
    dump_contract_abi(tkn.abi, 'exchange', name)
    add[name]['exchange'] = tkn.address
    dump_addresses(add)
    return tkn


def deploy_Challenge(name, own, cnt, tkn_PaC, exc_team):
    """
    - deploy AMPM Challenge, using payCoin token and exchange team
    - save abi and address
    """
    sprint(f"IDEV: Deploy {name} Challenge as {name}")
    tkn = own.deploy(cnt, tkn_PaC, exc_team)
    eprint()
    dump_contract_abi(tkn.abi, 'challenge', name)
    add = load_addresses()
    add[name]['challenge'] = tkn.address
    dump_addresses(add)
    return tkn


def add_mb_GERC20(name, own, tkn):
    """add minters and burners of team token exchange team only"""
    add = load_addresses()
    sprint(f"IDEV: Add Exchange of {name} as minters of {name[2:]}")
    tkn.addMinter(add[name]['exchange'], {'from': own})
    eprint()
    sprint(f"IDEV: Add Exchange of {name} as burners of {name[2:]}")
    tkn.addBurner(add[name]['exchange'], {'from': own})
    eprint()


def add_cst_cteam(name, own, tkn_dict):
    """add AMPM-ORG as customer of exchange, challenge of other teams"""
    add = load_addresses()
    sprint(f"IDEV: Add AMPM-ORG as customer of {name} exchange,challenge")
    tkn_dict['exchange'].addCustomer(add['AMPM-ORG']['address'], {'from': own})
    tkn_dict['challenge'].addCustomer(
        add['AMPM-ORG']['address'], {'from': own})
    eprint()


def add_mng_cteam(name, own, tkn):
    """add Challenge of a tema as manager of relative exchange"""
    add = load_addresses()
    sprint(f"IDEV: Add challenge of {name} as manager of {name} exchange")
    tkn.addManager(add[name]['challenge'], {'from': own})
    eprint()


def check_cst_cteam(name, tkn_dict):
    """
    Check if AMPM-ORG is customer of exchange,
    challenge of others team <name>
    """
    add = load_addresses()
    sprint(f"I: Check if AMPM-ORG is customer of exchange, " +
           f"challenge of {name}")
    for type in ['exchange', 'challenge']:
        print(f"Is AMPM-ORG customer of {type} {name}?", end=' ')
        bCustomer = tkn_dict[type].isCustomer(add['AMPM-ORG']['address'])
        print("Yes, it is") if bCustomer else print("No, it isn't")
    eprint()


def load_Contract(name, own, type):
    """
    reload contract <type> of team <name> as AMPM-ORG
    using abi and address
    """
    add = load_addresses()
    sprint(f"I: Load contract {type} of {name}")
    print("Loading ... ", end='')
    tkn = Contract.from_abi(type.title(
    )+name, add[name][type], load_contract_abi(type, name),
        owner=own)
    print("ok")
    eprint()
    return tkn


def deploy_AMPM(own, cnt):
    """
    - deploy AMPM token
    - save abi and address
    """
    sprint("I: Deploy AMPM token as AMPM-ORG")
    tkn = own.deploy(cnt)
    eprint()
    dump_contract_abi(tkn.abi, 'token', 'AMPM-ORG')
    add = load_addresses()
    add['AMPM-ORG']['token'] = tkn.address
    dump_addresses(add)
    return tkn


def deploy_ExchangeAMPM(own, cnt, tkn_PaC, tkn_AMPM):
    """
    - deploy AMPM Exchange, using AMPM payCoin token
    - save abi and address
    """
    add = load_addresses()
    sprint("I: Deploy AMPM Exchange")
    tkn = own.deploy(cnt, get_init_price(), tkn_PaC, tkn_AMPM)
    eprint()
    dump_contract_abi(tkn.abi, 'exchange', 'AMPM-ORG')
    add['AMPM-ORG']['exchange'] = tkn.address
    dump_addresses(add)
    return tkn


def deploy_ChallengeAMPM(own, cnt, tkn_PaC, exc_AMPM):
    """
    - deploy AMPM Challenge, using payCoin token and exchangeAMPM
    - save abi and address
    """
    sprint("I: Deploy AMPM Challenge")
    tkn = own.deploy(cnt, tkn_PaC, exc_AMPM)
    eprint()
    dump_contract_abi(tkn.abi, 'challenge', 'AMPM-ORG')
    add = load_addresses()
    add['AMPM-ORG']['challenge'] = tkn.address
    dump_addresses(add)
    return tkn


def add_mb_AMPM(own, tkn):
    """add minters and burners of MPM exchangeAMPM only"""
    add = load_addresses()
    sprint("I: Add ExchangeAMPM as minters of MPM")
    tkn.addMinter(add['AMPM-ORG']['exchange'], {'from': own})
    eprint()
    sprint("I: Add ExchangeAMPM as burners of MPM")
    tkn.addBurner(add['AMPM-ORG']['exchange'], {'from': own})
    eprint()


def add_cst_AMPM(own, tkn_dict):
    """enable other team to interact with exchange, challenge"""
    add = load_addresses()
    sprint("I: Add other teams as customer of ExchangeAMPM,ChallengeAMPM")
    for add_name in add:
        if add_name in ['referee', 'payCoin', 'Lender', 'AMPM-ORG']:
            None
        else:
            tkn_dict['exchange'].addCustomer(
                add[add_name]['address'], {'from': own})
            tkn_dict['challenge'].addCustomer(
                add[add_name]['address'], {'from': own})
    eprint()


def add_mng_AMPM(own, tkn):
    """add ChallengeAMPM as manager of ExchangeAMPM"""
    add = load_addresses()
    sprint("I: Add ChallengeAMPM as manager of ExchangeAMPM")
    tkn.addManager(add['AMPM-ORG']['challenge'], {'from': own})
    eprint()


def load_ContractAMPM(own, type):
    """
    load AMPM contract type, different beaviour
    - development, from_abi(...)
    - ropsten, using Contract(address)
    """
    add = load_addresses()
    if get_network_name() == 'development':
        sprint(f"I: Load AMPM {type}")
        print("Loading ... ", end='')
        tkn = Contract.from_abi(type.title(
        )+'AMPM', add['AMPM-ORG'][type], load_contract_abi(type, 'AMPM-ORG'),
            owner=own)
        print("ok")
        eprint()
        return tkn
    else:
        sprint(f"I: Load AMPM {type}")
        print("Loading ... ", end='')
        tkn = Contract(add['AMPM-ORG'][type], owner=own)
        print("ok")
        eprint()
        return tkn


def load_payCoin(own=None):
    """load payCoin from_abi"""
    add = load_addresses()
    sprint("I: Load payCoin token")
    print("Loading ... ", end='')
    tkn = Contract.from_abi(
        'payCoin', add['payCoin'], load_contract_abi('payCoin'), owner=own)
    print("ok")
    eprint()
    return tkn


def load_Lender(own=None):
    """load Lender from_abi"""
    add = load_addresses()
    sprint("I: Load Lender")
    print("Loading ... ", end='')
    tkn = Contract.from_abi(
        'Lender', add['Lender'], load_contract_abi('Lender'), owner=own)
    print("ok")
    eprint()
    return tkn


def add_mb_payCoin(own, tkn, lacts):
    """
    add minters and burners of PaC
    exchange, challenge of all teams + Lender
    """
    add = load_addresses()
    sprint("IDEV: Add minters of PaC (teams+Lender)")
    for act in lacts:
        tkn.addMinter(add[act]['exchange'], {'from': own})
        tkn.addMinter(add[act]['challenge'], {'from': own})
    tkn.addMinter(add['Lender'], {'from': own})
    eprint()
    sprint("IDEV: Add burners of PaC (teams+Lender)")
    for act in lacts:
        tkn.addBurner(add[act]['exchange'], {'from': own})
        tkn.addBurner(add[act]['challenge'], {'from': own})
    tkn.addBurner(add['Lender'], {'from': own})
    eprint()


def add_cst_Lender(own, tkn, lacts):
    """add teams as customer of Lender"""
    add = load_addresses()
    sprint("IDEV: Add customer of Lender (all teams)")
    for act in lacts:
        tkn.addCustomer(add[act]['address'], {'from': own})
    eprint()


def check_cst_Lender(tkn):
    """Check if AMPM-ORG is customer of Lender"""
    add = load_addresses()
    sprint("I: Check if AMPM-ORG is customer of Lender")
    print("Is AMPM-ORG customer of Lender?", end=' ')
    bCustomer = tkn.isCustomer(add['AMPM-ORG']['address'])
    print("Yes, it is") if bCustomer else print("No, it isn't")
    eprint()


def refill_teams(own, tkn, lacts):
    """refill team wallets with 50k PaC"""
    add = load_addresses()
    sprint("IDEV: refill team wallets with 50k PaC")
    for act in lacts:
        tkn.mint(add[act]['address'], 50000*1e18, {'from': own})
    eprint()


def check_PaC_balance(tkn):
    """check PaC balance of teams"""
    add = load_addresses()
    sprint("I: Check PaC balances")
    for add_name in add.keys():
        if add_name in ['referee', 'payCoin', 'Lender']:
            None
        else:
            add_balance = tkn.balanceOf(add[add_name]['address'])
            print(f"{add_name} balance: {sci(add_balance)} PaC")
    eprint()


def check_mb_token(tkn, name):
    """check if ExchangeAMPM, ChallengeAMPM are MB of name"""
    add = load_addresses()
    sprint(f"I: Check if ExchangeAMPM, ChallengeAMPM are MB of {name}")
    for type in ['exchange', 'challenge']:
        print(f"Is {type} AMPM a {name} Minter?", end=' ')
        bMinter = tkn.isMinter(add['AMPM-ORG'][type])
        print("Yes, it is") if bMinter else print("No, it isn't")
    for type in ['exchange', 'challenge']:
        print(f"Is {type} AMPM a {name} Burner?", end=' ')
        bBurner = tkn.isBurner(add['AMPM-ORG'][type])
        print("Yes, it is") if bBurner else print("No, it isn't")
    eprint()


def check_mng_AMPM(tkn):
    """Check if challenge AMPM is a manager of exchange AMPM"""
    add = load_addresses()
    sprint("I: Check if ChallengeAMPM is a manager of Exchange AMPM")
    print("Is challenge AMPM a manager of exchange AMPM?", end=' ')
    bManager = tkn.isManager(add['AMPM-ORG']['challenge'])
    print("Yes, it is") if bManager else print("No, it isn't")
    eprint()


def check_cst_AMPM(tkn_dict):
    """Check if other teams are customers of exchange, challenge AMPM"""
    add = load_addresses()
    sprint("I: Check if other teams are customers of exchange, challenge AMPM")
    for add_name in add:
        if add_name in ['referee', 'payCoin', 'Lender', 'AMPM-ORG']:
            None
        else:
            for type in ['exchange', 'challenge']:
                print(f"Is {add_name} customer of {type} AMPM?", end=' ')
                bCustomer = tkn_dict[type].isCustomer(add[add_name]['address'])
                print("Yes, it is") if bCustomer else print("No, it isn't")
    eprint()


def reload_all_Contract(own):
    """reload all Contract as own"""
    cnt_dict = create_cnt_dict()
    for name in cnt_dict.keys():
        if name == 'payCoin':
            cnt_dict[name] = load_payCoin(own)
        elif name == 'Lender':
            cnt_dict[name] = load_Lender(own)
        elif name == 'AMPM-ORG':
            for type in cnt_dict[name].keys():
                cnt_dict[name][type] = load_ContractAMPM(own, type)
        else:
            for type in cnt_dict[name].keys():
                cnt_dict[name][type] = load_Contract(name, own, type)
    return cnt_dict


def flush_addresses_abis():
    """flush addresses and abis current network"""
    add = load_addresses()
    for add_name in add:
        if add_name in ['referee', 'payCoin', 'Lender']:
            add[add_name] = ''
        else:
            for key in add[add_name].keys():
                add[add_name][key] = ''
    dump_addresses(add)
    for item in os.listdir(f"abis/{get_network_name()}/"):
        if item in ['AMPM-ORG', 'TEAMF', 'TEAMM']:
            for file in os.listdir(f"abis/{get_network_name()}/{item}/"):
                if file.endswith(".json"):
                    os.remove(f"abis/{get_network_name()}/{item}/{file}")
        else:
            if item.endswith(".json"):
                os.remove(f"abis/{get_network_name()}/{item}")


def add_mb_referee(own, tkn, ladd):
    """
    add for safety MB of PaC other team referee
    and master referee
    """
    sprint("IDEV: Add team referee and master referee as MB of PaC")
    for add in ladd:
        tkn.addMinter(add, {'from': own})
        tkn.addBurner(add, {'from': own})
    eprint()
