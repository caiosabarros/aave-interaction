1. Transform our ETH to WETH:
  WETH is the ERC20 token form of ETH, so it can interact with the other ERC20 tokens in AAVE, Uniswap, etc.
2. Deposit ETH
3. Borrow some other token
4. Pay it back!

Important notes:
 >We do not to use an oracle this time, i.e., we are not calling any API from Chainlink, OppenZeppellin, etc: like the VRF, PriceFeeds, etc. Then, for integration testing, we can use the network Kovan and for unit tests we can use the mainnet-fork-dev. Therefore, we do not need any mocks, since we can use the network and for the local network we can mock the entire ETH ecosystem by forking it. 
 >When interacting with a contract, we surely need its address and its ABI. There are many ways to find the address of a contract, like Etherscan, or in the docs in the website of the protocol we want to work with.
 The thing is: the ABI can be found simply by importing the interface of that specific contrace :)
 >You'll see some lines commented out on the dependencies. If I let it be that, the brownie would download all
 the chainlink repository in order to refer to the files I want to use. The thing is that the repository is gigantic! It was taking so much time. I just put the low-level code without importing it in there. So, it went well!