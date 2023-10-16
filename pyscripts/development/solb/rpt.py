# --------------------------------------------
# RPT.PY -------------------------------------
# --------------------------------------------
# Report functions
# --------------------------------------------
# --------------------------------------------

from brownie import network, web3
from solb.util import connect_network
from solb.iod import load_addresses, load_events
from solb.mnt import get_logs
import datetime



global files
files = {}

global trading
trading = { '0xe5e619C1cE24A3c5083D6c30FAD80Dbe4D8FFd39'.lower() : 'AMPM-ORG',
            '0x27C404d4D91156F7063E8dB9cC10970cfffF9a6C'.lower(): 'TEAMM',
            '0xe6a2234764Bd7a41Da73bd91F9E857819d20b22F'.lower(): 'TEAMF' }

global challenge
challenge = { '0x20BBCe5ee9Bc741C4560BC2985D008c4654978ED' : 'AMPM-ORG',
            '0x1d935B72E9AC4823BA0e1D71f70DFE51836858fF': 'TEAMM',
            '0x0b6019c547Ba293eBD74991217354b1281209985': 'TEAMF' }

global first, last
first = 8158412
last = 8200717

def open_files(filename):
    files['AMPM-ORG'] = open(f"data/AMPM-{filename}.txt", 'w')
    files['TEAMM'] = open(f"data/TEAMM-{filename}.txt", 'w')
    files['TEAMF'] = open(f"data/TEAMF-{filename}.txt", 'w')
    files['bug'] = open(f"data/BUG-{filename}.txt", 'w')

def close_files():
    for el in list(files.keys()):
        files[el].close()


def get_full_data(event, *args):
    ret = []
    block = web3.eth.getBlock(event['blockNumber'])
    ret.append(datetime.datetime.fromtimestamp(
        block['timestamp']))
    ret.append(event['address'])
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

# Challenge related ******************************************************
def plotly_challenge():
    ev_dict = load_events()
    act_dict = load_addresses()
    for act in list(act_dict.keys())[-3:]:
        for event in list(ev_dict['challenge'].keys())[:2]:
            emitted = get_logs(act_dict[act]['challenge'], first, last, signature=ev_dict['challenge'][event])
            for log in emitted:
                if event == 'direct':
                    scrap = get_full_data(log, 'address','address','uint256')
                    if scrap[3].lower() in list(trading.keys()) and scrap[2].lower() in list(trading.keys()):
                        files[ trading[scrap[2]] ].write(f'{event.upper()}\t{scrap[0]}\t{scrap[1]}\t{scrap[2]}\t{scrap[3]}\t{scrap[4]}\n')
                    else:
                        files['bug'].write(f'{event.upper()}\t{scrap[0]}\t{scrap[1]}\t{scrap[2]}\t{scrap[3]}\t{scrap[4]}\n')
                elif event == 'team':
                    scrap = get_full_data(log, 'address','uint256')
                    if scrap[2].lower() in list(trading.keys()):
                        files[ trading[scrap[2]] ].write(f'{event.upper()}\t{scrap[0]}\t{scrap[1]}\t{scrap[2]}\t{None}\t{scrap[3]}\n')
                    else:
                        files['bug'].write(f'{event.upper()}\t{scrap[0]}\t{scrap[1]}\t{scrap[2]}\t{None}\t{scrap[3]}\n')


def plotly_win_challenge():
    ev_dict = load_events()
    act_dict = load_addresses()
    for act in list(act_dict.keys())[-3:]:
        for event in list(ev_dict['challenge'].keys())[-3:]:
            emitted = get_logs(act_dict[act]['challenge'], first, last, signature=ev_dict['challenge'][event])
            for log in emitted:
                if event == 'won_direct':
                    scrap = get_full_data(log, 'address','uint256','uint256')
                    files[ trading[scrap[2]] ].write(f'{event.upper()}\t{scrap[0]}\t{scrap[1]}\t{scrap[2]}\t{scrap[3]}\t{scrap[4]}\n')
                elif event == 'won_team':
                    scrap = get_full_data(log, 'address','uint256', 'uint256')
                    files[ trading[scrap[2]] ].write(f'{event.upper()}\t{scrap[0]}\t{scrap[1]}\t{scrap[2]}\t{scrap[3]}\t{scrap[4]}\n')
                elif event == 'won_overnight':
                    scrap = get_full_data(log, 'address','uint256')
                    files[ trading[scrap[2]] ].write(f'{event.upper()}\t{scrap[0]}\t{scrap[1]}\t{scrap[2]}\t{scrap[3]}\n')


def plotly_register():
    ev_dict = load_events()
    act_dict = load_addresses()
    event = list(ev_dict['challenge'].keys())[2]
    for act in list(act_dict.keys())[-3:]:
        emitted = get_logs(act_dict[act]['challenge'], first, last, signature=ev_dict['challenge'][event])
        for log in emitted:
            scrap = get_full_data(log, 'address')
            if scrap[2].lower() in list(trading.keys()):
                files[ challenge[scrap[1]] ].write(f'{event.upper()}\t{scrap[0]}\t{scrap[1]}\t{scrap[2]}\n')
            else:
                files['bug'].write(f'{event.upper()}\t{scrap[0]}\t{scrap[1]}\t{scrap[2]}\n')

# Exchange related *******************************************************

def plotly_buy_sell():
    ev_dict = load_events()
    act_dict = load_addresses()
    for act in list(act_dict.keys())[-3:]:
        for event in list(ev_dict['exchange'].keys())[1:3]:
            emitted = get_logs(act_dict[act]['exchange'], first, last, signature=ev_dict['exchange'][event])
            for log in emitted:
                if event == 'buy':
                    try:
                        scrap = get_full_data(log, 'address','uint256','uint256')
                        files[ trading[scrap[2]] ].write(f'{event.upper()}\t{scrap[0]}\t{scrap[1]}\t{scrap[2]}\t{scrap[3]}\t{scrap[4]}\n')
                    except:
                        files['bug'].write(f'{event.upper()}\t{scrap[0]}\t{scrap[1]}\t{scrap[2]}\t{scrap[3]}\t{scrap[4]}\n')
                elif event == 'sell':
                    try:
                        scrap = get_full_data(log, 'address','uint256', 'uint256')
                        files[ trading[scrap[2]] ].write(f'{event.upper()}\t{scrap[0]}\t{scrap[1]}\t{scrap[2]}\t{scrap[3]}\t{scrap[4]}\n')
                    except:
                        files['bug'].write(f'{event.upper()}\t{scrap[0]}\t{scrap[1]}\t{scrap[2]}\t{scrap[3]}\t{scrap[4]}\n')

# Lender related *******************************************************

def plotly_loan():
    ev_dict = load_events()
    act_dict = load_addresses()
    act = act_dict['Lender']
    for event in list(ev_dict['Lender'].keys()):
        emitted = get_logs(act, first, last, signature=ev_dict['Lender'][event])
        for log in emitted:
            if event == 'open':
                try:
                    scrap = get_full_data(log, 'address','uint256','uint256')
                    files[ trading[scrap[2]] ].write(f'{event.upper()}\t{scrap[0]}\t{scrap[1]}\t{scrap[2]}\t{scrap[3]}\t{scrap[4]}\n')
                except:
                    files['bug'].write(f'{event.upper()}\t{scrap[0]}\t{scrap[1]}\t{scrap[2]}\t{scrap[3]}\t{scrap[4]}\n')
            elif event == 'close':
                try:
                    scrap = get_full_data(log, 'address','uint256')
                    files[ trading[scrap[2]] ].write(f'{event.upper()}\t{scrap[0]}\t{scrap[1]}\t{scrap[2]}\t{None}\t{scrap[3]}\n')
                except:
                    files['bug'].write(f'{event.upper()}\t{scrap[0]}\t{scrap[1]}\t{scrap[2]}\t{None}\t{scrap[3]}\n')

# AMPM related *******************************************************

def plotly_MB_token():
    ev_dict = load_events()
    act_dict = load_addresses()
    event = ev_dict['payCoin']['MB']
    for act in list(act_dict.keys())[-3:]:
        emitted = get_logs(act_dict[act]['token'], first, last, signature=event)
        for log in emitted:
            scrap = get_full_data(log, 'address','address','uint256')
            if scrap[2] == '0x0':
                tx = 'mint'
                try:
                    files[ trading[scrap[3]] ].write(f'{tx.upper()}\t{scrap[0]}\t{scrap[1]}\t{scrap[2]}\t{scrap[3]}\t{scrap[4]}\n')
                except:
                    files['bug'].write(f'{tx.upper()}\t{scrap[0]}\t{scrap[1]}\t{scrap[2]}\t{scrap[3]}\t{scrap[4]}\n')
            elif scrap[3] == '0x0':
                tx = 'burn'
                try:
                    files[ trading[scrap[2]] ].write(f'{tx.upper()}\t{scrap[0]}\t{scrap[1]}\t{scrap[2]}\t{scrap[3]}\t{scrap[4]}\n')
                except:
                    files['bug'].write(f'{tx.upper()}\t{scrap[0]}\t{scrap[1]}\t{scrap[2]}\t{scrap[3]}\t{scrap[4]}\n')

# PayCoin related *******************************************************

def plotly_MB_payCoin():
    ev_dict = load_events()
    act_dict = load_addresses()
    event = ev_dict['payCoin']['MB']
    act = act_dict['payCoin']
    emitted = get_logs(act, first, last, signature=event)
    for log in emitted:
        scrap = get_full_data(log, 'address','address','uint256')
        if scrap[2] == '0x0':
            tx = 'mint'
            try:
                files[ trading[scrap[3]] ].write(f'{tx.upper()}\t{scrap[0]}\t{scrap[1]}\t{scrap[2]}\t{scrap[3]}\t{scrap[4]}\n')
            except:
                files['bug'].write(f'{tx.upper()}\t{scrap[0]}\t{scrap[1]}\t{scrap[2]}\t{scrap[3]}\t{scrap[4]}\n')
        elif scrap[3] == '0x0':
            tx = 'burn'
            try:
                files[ trading[scrap[2]] ].write(f'{tx.upper()}\t{scrap[0]}\t{scrap[1]}\t{scrap[2]}\t{scrap[3]}\t{scrap[4]}\n')
            except:
                files['bug'].write(f'{tx.upper()}\t{scrap[0]}\t{scrap[1]}\t{scrap[2]}\t{scrap[3]}\t{scrap[4]}\n')
        else:
            tx = 'transferFrom'
            files['bug'].write(f'{tx.upper()}\t{scrap[0]}\t{scrap[1]}\t{scrap[2]}\t{scrap[3]}\t{scrap[4]}\n')
