from brownie import network
from solb.util import connect_network
from solb.rpt import plotly_buy_sell, get_full_data, open_files, close_files

if __name__ == '__main__':

    try:

        # check/connect network states
        connect_network()

        open_files('buy-sell')

        # Search and catalog in files exchange-(buy + sell) events
        plotly_buy_sell()

        close_files()

    except Exception as cerr:

        print(cerr)

        # kill rpc local connection
        network.disconnect()
