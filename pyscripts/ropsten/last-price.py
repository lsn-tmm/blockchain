# --------------------------------------------
# LAST-PRICE.PY ------------------------------
# --------------------------------------------
# Run change last price automation,
# with logging
# --------------------------------------------
# --------------------------------------------

from brownie import network, project
from solb.util import connect_network, load_act_from_prv_key
from solb.iod import reload_all_Contract
from solb.mnt import last_price

if __name__ == '__main__':

    try:

        # check/connect network states
        connect_network()

        # load brownie project
        prj = project.load()

        # load local AMPM account
        act = load_act_from_prv_key("AMPM-ORG")

        # Reload contracts with AMPM-ORG account as owner
        cnt_dict = reload_all_Contract(act)

        # Last price loop
        last_price(cnt_dict)

    except Exception:

        # close project
        prj.close()

        # kill rpc local connection
        network.disconnect()
