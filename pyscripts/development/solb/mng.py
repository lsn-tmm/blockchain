# --------------------------------------------
# MNG.PY -------------------------------------
# --------------------------------------------
# Management functions (Exchange + Challenge)
# --------------------------------------------
# --------------------------------------------

import time
import datetime
import sys
from pandas import read_csv, DataFrame
from numpy.random import randint
from numpy import nan, asarray
from solb.util import setup_logger, get_network_name, sci
from solb.iod import load_addresses
from brownie.network import web3

mnglogger = setup_logger('management',
                         f"pyscripts/{get_network_name()}/logs/management.log")


def change_start(tkn, year, month, day, hour, minute, own=None):
    """change timestamp start from date(UTC)"""
    date = int(datetime.datetime(year, month, day, hour, minute).timestamp())
    if own:
        tkn.changeStart(date, {'from': own})
    else:
        tkn.changeStart(date)
    mnglogger.warning(f"(change_start) Changed start: {date}")


def change_start_to_now(tkn, own=None):
    """change timestamp start from now(UTC)"""
    now = datetime.datetime.now(datetime.timezone.utc)
    change_start(tkn, now.year, now.month, now.day, now.hour, now.minute, own)


def change_end(tkn, year, month, day, hour, minute, own=None):
    """change timestamp end from date(UTC)"""
    date = int(datetime.datetime(year, month, day, hour, minute).timestamp())
    if own:
        tkn.changeEnd(date, {'from': own})
    else:
        tkn.changeEnd(date)
    mnglogger.warning(f"(change_end) Changed end: {date}")


def change_end_to_now(tkn, own=None):
    """change timestamp end from now(UTC)"""
    now = datetime.datetime.now(datetime.timezone.utc)
    change_end(tkn, now.year, now.month, now.day, now.hour, now.minute, own)


def change_price(tkn):
    """
    change price using price.history increments
    ONLY if the market is open (07-16 UTC)
    """
    mnglogger.info("(change_price) Price change start")
    try:
        incr = read_csv(
            f"pyscripts/{get_network_name()}/price.prv.history", header=None,
            names=['p'])['p']
        while True:
            if tkn.isOpen():
                wait = randint(5, 10, 1)[0]*60 + randint(0, 60, 1)[0]
                time.sleep(wait)
                id, price = tkn.lastPrice()
                tkn.priceChange(incr[id+1])
                id_new, price_new = tkn.lastPrice()
                mnglogger.info(
                    "(change_price) Price changed, " +
                    f"({id},{sci(price)}) | " +
                    f"({id_new},{sci(price_new)})")
            else:
                now = datetime.datetime.now(datetime.timezone.utc)
                if (now.hour < 6 or now.hour >= 16):
                    mnglogger.info(
                        "(change_price) Market is certainly closed, " +
                        "check opening every hour")
                    time.sleep(3600 - (now.minute*60 + now.second))
                elif (now.hour == 6 and now.minute < 50):
                    mnglogger.info(
                        "(change_price) Market is about to open, " +
                        "check opening every 10 minutes")
                    time.sleep(10*60 - now.second)
                elif (now.hour == 6 and now.minute >= 50):
                    mnglogger.info(
                        "(change_price) Market is opening, " +
                        "check opening every 1 minutes")
                    time.sleep(60 - now.second)
                elif (now.hour == 7):
                    mnglogger.info(
                        "(change_price) Market should be open, " +
                        "waiting clock offset, check every 10 seconds")
                    time.sleep(10 - (now.second % 10))
                else:
                    mnglogger.info(
                        "(change_price) Market must be open now, " +
                        "something wrong happened")
    except Exception:
        mnglogger.error("(change_price) Price change stopped",
                        exc_info=True)
        sys.exit(1) if get_network_name() == 'ropsten' else None


def load_price_pub(tkn):
    """load price pub history"""
    mnglogger.info("(load_price_pub) Load pub price start")
    try:
        incr = read_csv(
            f"pyscripts/{get_network_name()}/price.history", header=None,
            names=['p'])['p']
        id, price = tkn.lastPrice()
        for prc in asarray(incr)[(id+1):]:
            tkn.priceChange(int(prc))
    except Exception:
        mnglogger.error("(load_price_pub) Load pub price stopped",
                        exc_info=True)
        sys.exit(1) if get_network_name() == 'ropsten' else None


def buy(cnt_dict, team, amount):
    """
    buy an <amount> of <team> token using:
    - <cnt_dict>['payCoin']['token'] to set the PaC allowance
    - <cnt_dict>[team]['exchange'] to make the buy
    - write to file inside mnts, to record purchase
    - resetting allowance in case of failure
    """
    try:
        add = load_addresses()
        id, price = cnt_dict[team]['exchange'].lastPrice()
        pac_allow = price*amount  # 1e18 * 1e-18
        pac_allow += pac_allow*(2./1000)
        cnt_dict['payCoin'].approve(
            add[team]['exchange'], int(pac_allow))
        cnt_dict[team]['exchange'].buy(amount*1e18)
        if team == 'TEAMF':
            df = DataFrame({'id': [id], 'TEAMF': [price], 'TEAMM': [nan]})
        elif team == 'TEAMM':
            df = DataFrame({'id': [id], 'TEAMF': [nan], 'TEAMM': [price]})
        else:
            None
        df.to_csv(f'pyscripts/{get_network_name()}/mnts/buy.history', mode='a',
                  header=None, index=None)
    except Exception:
        cnt_dict['payCoin'].approve(add[team]['exchange'], 0)
        mnglogger.error(
            f"(buy) From ({team},{sci(amount*1e18)}) Errors", exc_info=True)
        sys.exit(1) if get_network_name() == 'ropsten' else None


def sell(cnt_dict, team, amount):
    """
    sell an <amount> of <team> token using:
    - <cnt_dict>[team]['token'] to set the team_tkn allowance
    - <cnt_dict>[team]['exchange'] to make the sell
    """
    try:
        add = load_addresses()
        id, price = cnt_dict[team]['exchange'].lastPrice()
        cnt_dict[team]['token'].approve(add[team]['exchange'], amount*1e18)
        cnt_dict[team]['exchange'].sell(amount*1e18)
        if team == 'TEAMF':
            df = DataFrame({'id': [id], 'TEAMF': [price], 'TEAMM': [nan]})
        elif team == 'TEAMM':
            df = DataFrame({'id': [id], 'TEAMF': [nan], 'TEAMM': [price]})
        else:
            None
        df.to_csv(f'pyscripts/{get_network_name()}/mnts/sell.history',
                  mode='a', header=None, index=None)
    except Exception:
        cnt_dict[team]['token'].approve(add[team]['exchange'], 0)
        mnglogger.error(
            f"(sell) To ({team},{sci(amount*1e18)}) Errors", exc_info=True)
        sys.exit(1) if get_network_name() == 'ropsten' else None


def overnight_start(cnt_dict, perc):
    """
    start overnight challenge:
    - <cnt_dict>['payCoin']['token'] to set the 200 PaC allowance
    - <cnt_dict>['AMPM-ORG']['challenge'] to startchallenge
    """
    try:
        add = load_addresses()
        id, price = cnt_dict['AMPM-ORG']['exchange'].lastPrice()
        cnt_dict['payCoin'].approve(
            add['AMPM-ORG']['challenge'], 200*1e18)
        cnt_dict['AMPM-ORG']['challenge'].overnightStart(perc)
        mnglogger.info(f"(overnight_start) Price changed by ({perc}%)")
        id_new, price_new = cnt_dict['AMPM-ORG']['exchange'].lastPrice()
        mnglogger.info("(overnight_start) Price changed, " +
                       f"({id},{sci(price)}) | ({id_new},{sci(price_new)})")
        return id_new
    except Exception:
        cnt_dict['payCoin'].approve(add['AMPM-ORG']['challenge'], 0)
        mnglogger.error(
            f"(overnight_start) Changing price ({perc}%) Errors",
            exc_info=True)
        return -1


def direct_challenge_start(cnt_dict, team):
    """
    start a direct challenge to <team>:
    - choosing a flag that hasn't yet been used
    - <cnt_dict>['AMPM-ORG']['challenge'] to record the challenged
      if not yet registered
    - <cnt_dict>['payCoin']['token'] to set the 50 PaC allowance
    - <cnt_dict>['AMPM-ORG']['challenge'] to startchallenge
    """
    try:
        add = load_addresses()
        flag = 0
        while True:
            if not cnt_dict['AMPM-ORG']['challenge'].directcheckFlag(flag):
                break
            flag += 1
        if cnt_dict['AMPM-ORG']['challenge'].isRegistered(
                add[team]['address']):
            None
        else:
            cnt_dict['AMPM-ORG']['challenge'].register(add[team]['address'])
        cnt_dict['payCoin'].approve(add['AMPM-ORG']['challenge'], 50*1e18)
        tx = cnt_dict['AMPM-ORG']['challenge'].challengeStart[
            'address,uint256'](add[team]['address'], flag)
        mnglogger.info(
            f"(direct_challenge_start) Direct started ({team},{flag})")
        time.sleep(3*60)
        tstamp = web3.eth.getBlock(tx.block_number)['timestamp']
        blk_now = datetime.datetime.fromtimestamp(
            tstamp, datetime.timezone.utc)
        cnt_dict['payCoin'].approve(add['AMPM-ORG']['challenge'], 50*1e18)
        now = datetime.datetime.now(datetime.timezone.utc)
        timer = (5*60 - (now - blk_now).seconds)
        timer = 1 if timer < 0 else timer
        return (flag, timer)
    except Exception:
        cnt_dict['payCoin'].approve(add['AMPM-ORG']['challenge'], 0)
        mnglogger.error(
            f"(direct_challenge_start) ({team},{flag}) Errors", exc_info=True)
        return (-1, 0)


def team_challenge_start(cnt_dict):
    """
    start a team challenge to all teams (our too):
    - choosing a flag that hasn't yet been used
    - <cnt_dict>['AMPM-ORG']['challenge'] to record only our team
      (other teams will have to arrange to register)
    - <cnt_dict>['payCoin']['token'] to set the 100 PaC allowance
    - <cnt_dict>['AMPM-ORG']['challenge'] to startchallenge
    """
    try:
        add = load_addresses()
        flag = 0
        while True:
            if not cnt_dict['AMPM-ORG']['challenge'].teamcheckFlag(flag):
                break
            flag += 1
        if cnt_dict['AMPM-ORG']['challenge'].isRegistered(
                add['AMPM-ORG']['address']):
            None
        else:
            cnt_dict['AMPM-ORG']['challenge'].register(
                add['AMPM-ORG']['address'])
        cnt_dict['payCoin'].approve(
            add['AMPM-ORG']['challenge'], 100*1e18)
        cnt_dict['AMPM-ORG']['challenge'].challengeStart['uint256'](flag)
        mnglogger.info(f"(team_challenge_start) Team started ({flag})")
        return flag
    except Exception:
        cnt_dict['payCoin'].approve(add['AMPM-ORG']['challenge'], 0)
        mnglogger.error(
            f"(team_challenge_start) ({flag}) Errors", exc_info=True)
        return -1


def overnight_check(cnt_dict, team, id, mul=1):
    """try to win overnight challenge"""
    try:
        up_gas_price = (mul*web3.eth.gasPrice)
        tx = cnt_dict[team]['challenge'].overnightCheck(
            id, {'gas_price': up_gas_price, 'gas_limit': 2.5e5})
        mnglogger.info(f"(overnight_check) You WIN it ({team}, {id}), " +
                       f"spending {tx.gas_used*up_gas_price} wei")
    except Exception:
        mnglogger.error(
            f"(overnight_check) ({team}, {id}) Errors", exc_info=True)


def direct_check(cnt_dict, team, flag, mul=1):
    """try to win direct challenge"""
    try:
        add = load_addresses()
        if cnt_dict[team]['challenge'].isRegistered(
                add['AMPM-ORG']['address']):
            None
        else:
            cnt_dict[team]['challenge'].register(
                add['AMPM-ORG']['address'])
        up_gas_price = (mul*web3.eth.gasPrice)
        if cnt_dict['payCoin'].allowance(add['AMPM-ORG']['address'],
                                         add[team]['challenge']) < (50*1e18):
            cnt_dict['payCoin'].approve(add[team]['challenge'], 50*1e18,
                                        {'gas_price': up_gas_price,
                                         'gas_limit': 5e5})
        else:
            None
        tx = cnt_dict[team]['challenge'].winDirectChallenge(
            flag, {'gas_price': up_gas_price, 'gas_limit': 5e5})
        if len(tx.events) > 2:
            mnglogger.info(f"(direct_check) You WIN it, " +
                           f"started by ({team}, {flag}), " +
                           f"spending {tx.gas_used*up_gas_price} wei")
        else:
            mnglogger.warning(f"(direct_check) You NOT WIN it, " +
                              f"started by ({team}, {flag}), too EARLY")
    except Exception:
        cnt_dict['payCoin'].approve(add[team]['challenge'], 0)
        mnglogger.error(
            f"(direct_check) Started by ({team}, {flag}) Errors",
            exc_info=True)


def team_check(cnt_dict, team, flag, mul=1):
    """try to win team challenge"""
    try:
        add = load_addresses()
        if cnt_dict[team]['challenge'].isRegistered(
                add['AMPM-ORG']['address']):
            None
        else:
            cnt_dict[team]['challenge'].register(
                add['AMPM-ORG']['address'])
        up_gas_price = (mul*web3.eth.gasPrice)
        cnt_dict['payCoin'].approve(add[team]['challenge'], 100*1e18,
                                    {'gas_price': up_gas_price,
                                     'gas_limit': 5e5})
        tx = cnt_dict[team]['challenge'].winTeamChallenge(
            flag, {'gas_price': up_gas_price, 'gas_limit': 5e5})
        if len(tx.events) > 2:
            mnglogger.info(f"(team_check) You WIN it, " +
                           f"started by ({team}, {flag}), " +
                           f"spending {tx.gas_used*up_gas_price} wei")
        else:
            mnglogger.warning(f"(team_check) You NOT WIN it, " +
                              f"started by ({team}, {flag}), too EARLY")
    except Exception:
        cnt_dict['payCoin'].approve(add[team]['challenge'], 0)
        mnglogger.error(
            f"(team_check) Started by ({team}, {flag}) Errors", exc_info=True)


def overnight_start_win(cnt_dict, perc, mul=1):
    """
    Automation of start + win overnight challenge:
    - start overnight challenge AMPM-ORG
    - wait 1 hour + 30 seconds (for safety)
    - try to win it
    """
    id = overnight_start(cnt_dict, perc)
    if id != -1:
        None
        # time.sleep(3600 + 30)
        # overnight_check(cnt_dict, 'AMPM-ORG', id, mul)
    else:
        sys.exit(1) if get_network_name() == 'ropsten' else None


def direct_start_win(cnt_dict, team, mul=1):
    """
    Automation of start + win direct challenge:
    - start direct challenge AMPM-ORG
    - wait 5 minutes + 30 seconds (for safety)
    - try to win it
    """
    flag, timer = direct_challenge_start(cnt_dict, team)
    if flag != -1:
        time.sleep(timer)
        direct_check(cnt_dict, 'AMPM-ORG', flag, mul)
    else:
        sys.exit(1) if get_network_name() == 'ropsten' else None


def team_start_win(cnt_dict, mul=1):
    """
    Automation of start + win team challenge:
    - start team challenge AMPM-ORG
    - wait 5 minutes + 30 seconds (for safety)
    - try to win it
    """
    flag = team_challenge_start(cnt_dict)
    if flag != -1:
        None
        # time.sleep(5*60 + 30)
        # team_check(cnt_dict, 'AMPM-ORG', flag, mul)
    else:
        sys.exit(1) if get_network_name() == 'ropsten' else None


def balance_digest(cnt_dict, team, act=None):
    """
    digest of balances:
    - wei (if act is not None)
    - PaC
    - MPM
    - AMF
    - AMM
    """
    add = load_addresses()
    ix = ['Wei', 'PaC', 'MPM', 'AMF', 'AMM']
    if act is None:
        ix = ix[1:]
        bal = [cnt_dict['payCoin'].balanceOf(add[team]['address']),
               cnt_dict['AMPM-ORG']['token'].balanceOf(add[team]['address']),
               cnt_dict['TEAMF']['token'].balanceOf(add[team]['address']),
               cnt_dict['TEAMM']['token'].balanceOf(add[team]['address'])]
        df = DataFrame(bal, columns=['balances'], index=ix)
        print(f"$ {team} $")
        print(df.to_string(formatters=(sci,)), end='\n\n')
    else:
        bal = [act.balance(),
               cnt_dict['payCoin'].balanceOf(add[team]['address']),
               cnt_dict['AMPM-ORG']['token'].balanceOf(add[team]['address']),
               cnt_dict['TEAMF']['token'].balanceOf(add[team]['address']),
               cnt_dict['TEAMM']['token'].balanceOf(add[team]['address'])]
        df = DataFrame(bal, columns=['balances'], index=ix)
        print(f"$ {team} $")
        print(df.to_string(formatters=(sci,)), end='\n\n')


def loan_open(cnt, amount):
    """
    open a loan to Lender contract as AMPM-ORG
    """
    try:
        tx = cnt.openLoan(amount*1e18)
        key = list(tx.events[1].keys())[-1]
        id = tx.events[1][key]
        mnglogger.info(
            f"(loan_open) Loan started at ({tx.block_number}," +
            f"{id},{amount*1e18})")
        if get_network_name() == 'development':
            return id
    except Exception:
        mnglogger.error(
            f"(loan_open) Loan ({tx.block_number}," +
            f"{id},{amount*1e18}) Errors",
            exc_info=True)
        sys.exit(1) if get_network_name() == 'ropsten' else None


def loan_close(cnt_dict, id):
    """
    close an opened loan using id
    """
    try:
        add = load_addresses()
        amount, fee = cnt_dict['Lender'].loanStatus(id)
        cnt_dict['payCoin'].approve(add['Lender'], amount+fee)
        tx = cnt_dict['Lender'].closeLoan(id)
        mnglogger.info(
            "(loan_close) Loan closed at " +
            f"({tx.block_number},{amount+fee})")
    except Exception:
        cnt_dict['payCoin'].approve(add['Lender'], 0)
        mnglogger.error(
            "(loan_close) Loan " +
            f"{tx.block_number},{amount+fee}) Errors",
            exc_info=True)
        sys.exit(1) if get_network_name() == 'ropsten' else None
