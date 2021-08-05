from brownie import Contract, chain
import requests
import json
import pandas as pd
import numpy as np
import os

# This is the script to recover how much was deposited and how much was withdrawn
# With emergency withdraw. Since it's quite long to gather the data, the script
# makes saves at each step.
# Result is in accounts_state.csv

# Result is in accounts_state.csv
# you can just open it then in Google Docs or Excel.

def main():
    # 0x26e9a3ec61044c38b4876ae33670e258f90c9f2bdf96b43c20dad4b2b0e5af9a tx where shit hit the fan
    # 9600772 last block before shit hit the fan
    
    # This is were we get all the tx that went through the Masterchef
    def get_tx_slice(startblock, endblock, step):
        txs_stash = list()
        id = 0
        for i in range(startblock, endblock, step):
            r = requests.get(f"https://api.bscscan.com/api?module=account&action=txlist&address=0xA3fDF7F376F4BFD38D7C4A5cf8AAb4dE68792fd4&startblock={i}&endblock={i+step}&page=1&sort=asc&apikey={API_KEY}")
            txs_stash.extend(r.json()["result"])
            print(f"startblock:{i}, endblock:{i+4999}, tx_stash:{len(txs_stash)}")
        print(len(txs_stash))

        return txs_stash

    # We check who interacted with the masterchef and could have a balance
    def get_addresses(filename):
        with open(filename, 'r') as f:
            data = json.load(f)
        
        addresses = set()
        for i in range(0,len(data)-1):
            addresses.add(data[i]["from"])
        
        df = pd.DataFrame(list(addresses), columns=["Addresses"])
        df.to_csv('addresses.csv', index=False)

    # We gather here transfers after the ownership was transfered and only EW was possible
    def get_withdraw_tx_by_bep20(bep20):
        df = pd.read_csv("addresses.csv")
        for token in bep20:
            token_name = token["name"]
            token_address = token["address"]
            df[f"amount_{token_name}"] = np.nan
            df[f"tx_list_{token_name}"] = ''
            for row in range(0,len(df)):
                txs_stash = list()
                address = df.loc[row,'Addresses']
                call = f"https://api.bscscan.com/api?module=account&action=tokentx&contractaddress={token_address}&address={address}&startblock=9600772&sort=asc&apikey={API_KEY}"
                r = requests.get(call)
                txs_stash.extend(r.json()["result"])

                amount_withdrawn = 0
                tx_list = []
                for tx in txs_stash:
                    if tx["from"] == "0xa3fdf7f376f4bfd38d7c4a5cf8aab4de68792fd4":
                        amount_withdrawn += int(tx["value"])
                        tx_list.append(tx["hash"])
                tx_strings = ','.join(tx_list)
                df.loc[df["Addresses"] == address, f"tx_list_{token_name}"] = tx_strings
                df.loc[df["Addresses"] == address, f"amount_{token_name}"] = amount_withdrawn/1e18
            df.to_csv('amounts.csv', index=False)

    def get_balances_before_hack(bep20):
        assert chain.height == 9600773
        with open("masterchef.abi", "r") as f:
            abi = json.load(f)
        chef = Contract.from_abi("MC", "0xA3fDF7F376F4BFD38D7C4A5cf8AAb4dE68792fd4", abi)
        # pool id: LI (3), DBI (4), SI (5)
        df = pd.read_csv('amounts.csv')
        for token in bep20_staked:
            token_name = token["name"]
            print(f"deposited_{token_name}")
            df[f"deposited_{token_name}"] = np.nan
            print(token["name"])
            for row in range(0,len(df)):
                address = df.loc[row,'Addresses']
                deposited, rewardDebt = chef.userInfo(token["pid"], address)
                df.loc[df["Addresses"] == address, f"deposited_{token_name}"] = deposited/1e18
                print(address + ' ' + str(deposited))
        df.to_csv('accounts_state.csv', index=False)

    # print("Get you key here: https://bscscan.com/login")
    # API_KEY = input("Please enter your Bscscan api key: ")
    # os.environ["BSCSCAN_TOKEN"] = API_KEY

    SI = {"name":"SI", "address": str.lower("0xA9102b07f1F577D7c58E481a8CbdB2630637Ea48"),"pid": 5}
    DBI ={"name":"DBI", "address": str.lower("0xB04c92A631c8c350Cf81b5b54A0FE8dfbCC68677"), "pid": 4}
    LI = {"name":"LI", "address": str.lower("0x08Ba8CCc71D92055e4b370283AE07F773211Cc29"), "pid": 3}
    bep20_staked = [DBI, LI, SI]
    
    # tx_data = get_tx_slice(7748604, 9687332, 20000)
    # with open('data.json', 'w') as f:
    #     f.write(json.dumps(tx_data))

    # get_addresses("data.json")
    # get_withdraw_tx_by_bep20(bep20_staked)
    # get_balances_before_hack(bep20_staked)





