from web3 import Web3
from scripts.helpful_scripts import get_account
from scripts.get_weth import get_weth
from brownie import config, interface, network

amount = Web3.toWei(0.1,"ether")

def get_lending_pool():
  #We need the address and the ABI of the Landing Pool contract.
  #We've gotten the ABI through its interface - since the interface compile down to the ABI -
  #And also the LendingPoolAddressesProvider interface,
  #since the first is dependable on the second.
  lending_pool_addresses_provider = interface.ILendingPoolAddressesProvider(
    config["networks"][network.show_active()]["lending_pool_addresses_provider"]
    )
  lending_pool_address = lending_pool_addresses_provider.getLendingPool() 
  #We've got the address, now let's get the ABI - just bring its interface.
  #We need then to refer its dependencies from the github - 9:13:00 on the video.
  lending_pool = interface.ILendingPool(lending_pool_address)
  return lending_pool

def approve_erc20(amount, spender, erc20_address,account):
  #approve(address spender, uint256 amount) → bool
  print("Approving ERC20")
  erc20_token = interface.IERC20(erc20_address)
  tx = erc20_token.approve(spender, amount, {"from":account})
  tx.wait(1)
  print("Approved spending of WETH!")
  return tx

def get_borrowble_data(lending_pool, account):
  ( 
    total_collateral_eth,
    total_debt_eth,
    available_borrow_eth,
    current_liquidation_threshold,
    ltv,
    health_factor
    ) = lending_pool.getUserAccountData(account.address)
  available_borrow_eth = Web3.fromWei(available_borrow_eth, "ether")
  total_collateral_eth = Web3.fromWei(total_collateral_eth, "ether")
  total_debt_eth = Web3.fromWei(total_debt_eth, "ether")
  print(f"You have {total_collateral_eth} worth of ETH deposited.")
  print(f"You have {total_debt_eth} worth of ETH borrowed.")
  print(f"You can borrow {available_borrow_eth} worth of ETH.")
  return (float(available_borrow_eth), float(total_debt_eth))

def get_asset_price(price_feed_address):
  #Does Bronwie already recognize Chainlink by default? Because idk why we did not need to refer to it
  # in the
  #dependencies.
  dai_eth_price_feed = interface.AggregatorV3Interface(price_feed_address)
  latest_price = dai_eth_price_feed.latestRoundData()[1]
  converted_latest_price = Web3.fromWei(latest_price, "ether")
  print(f"The DAI/ETH price is {converted_latest_price}")
  return float(converted_latest_price)

def repay_all(amount, lending_pool, account):
    approve_erc20(
        Web3.toWei(amount, "ether"),
        lending_pool,
        config["networks"][network.show_active()]["dai_token"],
        account,
    )
    repay_tx = lending_pool.repay(
        config["networks"][network.show_active()]["dai_token"],
        amount,
        1,
        account.address,
        {"from": account},
    )
    repay_tx.wait(1)
    print("Repaid!")


def main():
  #Let's start depositing. For that, we need to approve() and deposit() functions from the LendingPool contract
  #Actually, the approve() is from ERC-20 contract
  account = get_account()
  lending_pool = get_lending_pool()
  erc20_address = config["networks"][network.show_active()]["weth_token"]
  
  #Without it, an error shows up: VirtualMachineError: revert: SafeMath: subtraction overflow because the lack of WETH
  if network.show_active() in ["mainnet-fork-dev"]:
        get_weth()

  #Approving
  #AAVE docs: This can be done via the standard ERC20 approve() method.
  #approve(address spender, uint256 amount) → bool
  #Sets amount as the allowance of spender over the caller’s tokens = I will approve AAVE to spend my money.
  approve_erc20(amount, lending_pool.address, erc20_address, account)
  #We just allowed AAVE to spend our WETH.

  #Now, we'll truly deposit our money into the protocol of AAVE through their LendingPool contract.
  #Noticed that for approval we used the ERC20 contract, not the AAVEs contract.
  #function deposit(address asset, uint256 amount, address onBehalfOf, uint16 referralCode)
  deposit_tx = lending_pool.deposit(
    erc20_address, amount, account.address, 0, {"from": account}
    )
  deposit_tx.wait(1)
  print("Deposited")

  print("Let's borrow!")
  print("Let's see how our finances are")
  #Let's get our data concerning borrowing 
  borrowable_eth, total_debt = get_borrowble_data(lending_pool, account)

  dai_eth_price = get_asset_price(
    config["networks"][network.show_active()]["dai_eth_price_feed"]
  )
  #0.95 means we'll borrow 95% of what we can. Also, to know dai_eth_price
  #We need the AggregatorV3Interface.sol from Chainlink 
  amount_dai_to_borrow = (1 / dai_eth_price) * (borrowable_eth * 0.95)
  print(f"We are going to borrow {amount_dai_to_borrow} DAI")

  dai_address = config["networks"][network.show_active()]["dai_token"]

  # function borrow( address asset, uint256 amount, uint256 interestRateMode, 
  # uint16 referralCode, address onBehalfOf) external;
  borrow_tx = lending_pool.borrow(
    dai_address, 
    Web3.toWei(amount_dai_to_borrow, "ether"), 
    1, #1 means StableInterestRateMode and 2 means VariableInsterestRateMode
    0, 
    account.address,
    {"from": account}
    )
  borrow_tx.wait(1)
  print("We borrowed some DAI!")
  print("Let's see how our finances are now")
  repay_all(amount, lending_pool, account)
  print(
        "You just deposited, borrowed, and repayed with Aave, Brownie, and Chainlink!"
  )



