from brownie import network
from solb.util import connect_network
from solb.rpt import plotly_register, get_full_data, open_files, close_files

if __name__ == '__main__':

    try:

        # check/connect network states
        connect_network()

        open_files('register')

        # Search for challenge register events
        plotly_register()

        close_files()

    except Exception as cerr:

        print(cerr)

        # kill rpc local connection
        network.disconnect()
