# --------------------------------------------
# LOAD-PUB-PRICE.PY --------------------------
# --------------------------------------------
# Run load pub price automation,
# with logging
# --------------------------------------------
# --------------------------------------------

from brownie import network, project
from solb.util import connect_network, load_act_from_prv_key
from solb.iod import reload_all_Contract
from solb.mng import load_price_pub

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

        # Load price pub history loop
        load_price_pub(cnt_dict['AMPM-ORG']['exchange'])

    except Exception:

        # close project
        prj.close()

        # kill rpc local connection
        network.disconnect()
