from scripts.helpful_scripts import get_account
from brownie import interface, config, network, accounts

def get_weth():
  account = get_account()
  #getting the weth contract from its interface
  weth = interface.IWeth(config["networks"][network.show_active()]["weth_token"]) 
  tx = weth.deposit({"from": account, "value": 0.1*10**18}) 
  #This deposit function is from the WETH smart contract interface, not from the AAVEs contracts
  tx.wait(1)
  print("It's been deposited 0.1 WETH")
  return tx





def main():
  get_weth()