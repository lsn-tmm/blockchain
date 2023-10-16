# --------------------------------------------
# READ-CHALLENGE-LOGS.PY ---------------------
# --------------------------------------------
# Run check challenge events (direct + team)
# automation, with logging
# --------------------------------------------
# --------------------------------------------

from brownie import network, project
from solb.util import connect_network
from solb.mnt import read_ch_logs

if __name__ == '__main__':

    try:

        # check/connect network states
        connect_network()

        # load brownie project
        prj = project.load()

        # Check challenge (direct + team) events
        read_ch_logs()

    except Exception:

        # close project
        prj.close()

        # kill rpc local connection
        network.disconnect()
