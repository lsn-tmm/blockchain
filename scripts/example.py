from brownie import network, accounts, Example


def main():
   if (network.show_active() == 'development'):
      act = accounts[0]
      tkn = act.deploy(Example)
      print(f"Smart contract operation: 2 + 5 = {tkn.sum(2,5)}", end='\n\n')
   else:
      print('\nNot implemented', end='\n\n')
