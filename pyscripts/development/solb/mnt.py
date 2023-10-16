# --------------------------------------------
# MNT.PY -------------------------------------
# --------------------------------------------
# Monitor functions
# --------------------------------------------
# --------------------------------------------

import time
import datetime
import sys
from subprocess import call
from solb.iod import load_addresses, load_events
from solb.util import setup_logger, get_network_name, write_args
from pandas import DataFrame
from brownie.network import web3

mntlogger = setup_logger('monitor',
                         f"pyscripts/{get_network_name()}/logs/monitor.log")


def last_price(cnt_dict):
    """
    lastprice.history recorder,
    ONLY if the market is open (07-16 UTC)
    """
    mntlogger.info("(last_price) Last price record started")
    try:
        id = {}
        price = {}
        while True:
            open = (cnt_dict['AMPM-ORG']['exchange'].isOpen() or
                    cnt_dict['TEAMF']['exchange'].isOpen() or
                    cnt_dict['TEAMM']['exchange'].isOpen())
            if open:
                for team in ['AMPM-ORG', 'TEAMF', 'TEAMM']:
                    tkn = cnt_dict[team]['exchange']
                    id[team], price[team] = tkn.lastPrice()
                for team in ['AMPM-ORG', 'TEAMF', 'TEAMM']:
                    df = DataFrame(
                        {'id': [id[team]], f'{team}': [price[team]]})
                    df.to_csv(f"pyscripts/{get_network_name()}/" +
                              f"mnts/lastprice-{team}.history", mode='a',
                              header=None, index=None)
                time.sleep(5*60)
            else:
                now = datetime.datetime.now(datetime.timezone.utc)
                if (now.hour < 6 or now.hour >= 16):
                    mntlogger.info(
                        "(last_price) Market is certainly closed, " +
                        "check opening every hour")
                    time.sleep(3600 - (now.minute*60 + now.second))
                elif (now.hour == 6 and now.minute < 50):
                    mntlogger.info(
                        "(last_price) Market is about to open, " +
                        "check opening every 10 minutes")
                    time.sleep(10*60 - now.second)
                elif (now.hour == 6 and now.minute >= 50):
                    mntlogger.info(
                        "(last_price) Market is opening, " +
                        "check opening every 1 minutes")
                    time.sleep(60 - now.second)
                elif (now.hour == 7):
                    mntlogger.info(
                        "(last_price) Market should be open, " +
                        "waiting clock offset, check every 10 seconds")
                    time.sleep(10 - (now.second % 10))
                else:
                    mntlogger.info(
                        "(last_price) Market must be open now, " +
                        "something wrong happened")
    except Exception:
        mntlogger.error("(last_price) Last price record stopped",
                        exc_info=True)
        sys.exit(1) if get_network_name() == 'ropsten' else None


def get_logs(address, from_block, to_block, signature,
             topic1=None, topic2=None, topic3=None):
    """wrapper around getLogs"""
    return web3.eth.getLogs({
                        "address": address,
                        "fromBlock": from_block,
                        "toBlock": to_block,
                        "topics": [signature, topic1, topic2, topic3]
                        })


def get_data_and_topics(event, *args):
    ret = []
    block = web3.eth.getBlock(event['blockNumber'])
    ret.append(datetime.datetime.fromtimestamp(
        block['timestamp'], datetime.timezone.utc))
    topic = event['topics'][1:]
    for x in range(len(topic)):
        if (args[x] == 'address'):
            ret.append(hex(int(topic[x].hex(), 16)))
        elif (args[x] == 'uint256'):
            ret.append(int(topic[x].hex(), 16))
    try:
        if type(len(event['data'])) == 'list':
            for data in event['data']:
                ret.append(int(data, 16))
        else:
            ret.append(int(event['data'], 16))
    except Exception:
        pass
    return ret


# -----------------------------------
# VOLATILE MEMORY BLOCK NUMBER
# -----------------------------------
global founded
founded = {}
founded['AMPM-ORG'] = {}
founded['TEAMM'] = {}
founded['TEAMF'] = {}
for team in list(founded.keys()):
    founded[team]['priceChange'] = set()
    founded[team]['direct'] = set()
    founded[team]['team'] = set()
# -----------------------------------


def read_ch_logs():
    try:
        act_dict = load_addresses()
        ev_dict = load_events()
        while True:
            emitted = {}
            last = web3.eth.getBlock('latest')['number']
            for act in list(act_dict.keys())[-2:]:
                emitted[act] = {}
                for event in list(ev_dict['challenge'].keys())[:2]:
                    emitted[act][event] = get_logs(
                        act_dict[act]['challenge'],  last-30, last-1,
                        signature=ev_dict['challenge'][event])
                    check = len(founded[act][event])
                    for log in emitted[act][event]:
                        founded[act][event].add(log['blockNumber'])
                    if (len(founded[act][event]) > check):
                        n = len(founded[act][event])-check
                        for log in emitted[act][event][-n:]:
                            if event == 'direct':
                                scrap = get_data_and_topics(
                                    log, 'address', 'address', 'uint256')
                                we = act_dict['AMPM-ORG']['address'].lower()
                                if (scrap[2] == we):
                                    now = datetime.datetime.now(
                                        datetime.timezone.utc)
                                    timer = (5*60 - (now-scrap[0]).seconds)
                                    timer = 1 if timer < 0 else timer
                                    write_args('pybot-direct-win', act,
                                               scrap[3], timer, 800)
                                    cmd = ("sudo systemctl start " +
                                           "pybot-direct-win.service")
                                    cmd = cmd.split(' ')
                                    val = call(cmd)
                                    if val:
                                        mntlogger.error("(read_ch_logs) " +
                                                        "Direct Win Service " +
                                                        "not started",
                                                        exc_info=True)
                                    else:
                                        mntlogger.info("(read_ch_logs) " +
                                                       "Direct Win Service " +
                                                       "started")
                            elif event == 'team':
                                scrap = get_data_and_topics(
                                    log, 'address', 'uint256')
                                now = datetime.datetime.now(
                                    datetime.timezone.utc)
                                timer = (20 + 5*60 - (now - scrap[0]).seconds)
                                timer = 1 if timer < 0 else timer
                                write_args('pybot-team-win', act,
                                           scrap[2], timer, 800)
                                cmd = ("sudo systemctl start " +
                                       "pybot-team-win.service")
                                cmd = cmd.split(' ')
                                val = call(cmd)
                                if val:
                                    mntlogger.error("(read_ch_logs) " +
                                                    "Team Win Service " +
                                                    "not started",
                                                    exc_info=True)
                                else:
                                    mntlogger.info("(read_ch_logs) " +
                                                   "Team Win Service " +
                                                   "started")
            time.sleep(4*60)
    except Exception:
        mntlogger.error("(read_ch_logs) Errors", exc_info=True)
        sys.exit(1) if get_network_name() == 'ropsten' else None


def read_pr_logs():
    try:
        act_dict = load_addresses()
        ev_dict = load_events()
        while True:
            emitted = {}
            last = web3.eth.getBlock('latest')['number']
            for act in list(act_dict.keys())[-3:]:
                emitted[act] = {}
                emitted[act]['priceChange'] = get_logs(
                    act_dict[act]['challenge'],  last-30, last-1,
                    signature=ev_dict['exchange']['priceChange'])
                check = len(founded[act]['priceChange'])
                for log in emitted[act]['priceChange']:
                    founded[act]['priceChange'].add(log['blockNumber'])
                if (len(founded[act]['priceChange']) > check):
                    n = len(founded[act]['priceChange'])-check
                    for log in emitted[act]['priceChange'][-n:]:
                        scrap = get_data_and_topics(
                            log, 'address', 'uint256', 'uint256')
                        write_args('pybot-overnight-win',
                                   act, scrap[2], 1, 10)
                        cmd = ("sudo systemctl start " +
                               "pybot-overnight-win.service")
                        cmd = cmd.split(' ')
                        val = call(cmd)
                        if val:
                            mntlogger.error("(read_pr_logs) " +
                                            "Team Win Service " +
                                            "not started",
                                            exc_info=True)
                        else:
                            mntlogger.info("(read_pr_logs) " +
                                           "Team Win Service " +
                                           "started")
            time.sleep(4*60)
    except Exception:
        mntlogger.error("(read_pr_logs) Errors", exc_info=True)
        sys.exit(1) if get_network_name() == 'ropsten' else None
