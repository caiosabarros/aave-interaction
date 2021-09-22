from brownie import config, network, accounts

FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-dev"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]

def get_account(index=None,id=None):
    if index: 
      return accounts[index] #it will return the an indexed account from local machine network
    if id:
      return accounts.load(id) #it will return an accounts saved in the local system
    if (
      network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
      or network.show_active() in FORKED_LOCAL_ENVIRONMENTS
    ):
      return accounts[0]
    return accounts.add(config["wallets"]["from_key"])