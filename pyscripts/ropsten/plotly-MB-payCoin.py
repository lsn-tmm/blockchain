from brownie import network
from solb.util import connect_network
from solb.rpt import plotly_MB_payCoin, get_full_data, open_files, close_files


if __name__ == '__main__':

    try:

        # check/connect network states
        connect_network()

        open_files('MB-payCoin')

        # Search and catalog in files token-(mint + burn) events
        plotly_MB_payCoin()

        close_files()

    except Exception as cerr:

        print(cerr)

        # kill rpc local connection
        network.disconnect()
