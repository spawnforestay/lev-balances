# lev-balances
How much was deposited on levyathan.finance and how much was withdrawn

# How to use this script?

1. Download everything - you'll need to install python3, [eth-brownie](https://eth-brownie.readthedocs.io/en/stable/install.html) in a virtualenv and install the packages needed in the ‘import‘ statements.

2. Get a free bsc archive node at [moralis.io](https://moralis.io/) - great service by the way.

3. Configure brownie - brownie will add a ‘.brownie‘ in the root folder, with a ‘network-config.yaml‘ file. Line 42, add those lines:

```yaml
- cmd: ganache-cli
  cmd_settings:
    accounts: 10
    evm_version: istanbul
    gas_limit: 12000000
    mnemonic: brownie
    port: 8545
    fork: https://speedy-nodes-nyc.moralis.io/YOUR_KEY/bsc/mainnet/archive@9600772
  host: http://127.0.0.1
  id: bsc-main-fork-archive
  name: Ganache-CLI (BSC-Mainnet Fork)
  timeout: 60
```

4. Go to [Bscscan](https://www.bscscan.com/login), sign in a grab an api key
5. In a clean folder, run `brownie init` - this will setup you environment
6. Paste the .py file in the `scripts` folder and the `.abi` file in the root of the project.
7. You can now run `brownie run scripts/recover-bal.py --network bsc-main-fork-archive -i`
8. The script should start. Wait for about an hour, as bscscan is slow, and check the results in `accounts_state.csv`
