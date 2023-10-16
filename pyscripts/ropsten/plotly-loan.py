from brownie import network
from solb.util import connect_network
from solb.rpt import plotly_loan, get_full_data, open_files, close_files


if __name__ == '__main__':

    try:

        # check/connect network states
        connect_network()

        open_files('loan')

        # Search and catalog in files lender-(open + close) loan events
        plotly_loan()

        close_files()

    except Exception as cerr:

        print(cerr)

        # kill rpc local connection
        network.disconnect()
