# --------------------------------------------
# READ-OVERNIGHT-LOGS.PY ---------------------
# --------------------------------------------
# Run check challenge events (overnight)
# automation, with logging
# --------------------------------------------
# --------------------------------------------

from brownie import network, project
from solb.util import connect_network
from solb.mnt import read_pr_logs

if __name__ == '__main__':

    try:

        # check/connect network states
        connect_network()

        # load brownie project
        prj = project.load()

        # Check challenge (overnight) events
        read_pr_logs()

    except Exception:

        # close project
        prj.close()

        # kill rpc local connection
        network.disconnect()
