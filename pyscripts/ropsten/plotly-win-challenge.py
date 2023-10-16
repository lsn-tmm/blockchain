from brownie import network
from solb.util import connect_network
from solb.rpt import plotly_win_challenge, get_full_data, open_files, close_files

if __name__ == '__main__':

    try:

        # check/connect network states
        connect_network()

        open_files('win-challenge')

        # Search and catalog in files challenge-winning events
        plotly_win_challenge()

        close_files()

    except Exception as cerr:

        print(cerr)

        # kill rpc local connection
        network.disconnect()
