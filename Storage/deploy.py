from pathlib import Path
from solcx import compile_standard, install_solc
import json
from web3 import Web3
import os
from dotenv import load_dotenv

# Prepare
load_dotenv()
install_solc("0.8.7")

# Read contract file
contract_path = Path(__file__).parent / "SimpleStorage.sol"
with open(contract_path, "r") as file:
    contract_file = file.read()

# Compile contract
compiled_contract = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": contract_file}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        },
    },
    solc_version="0.8.7",
)

# Write compiled contract to file
compiled_contract_json_path = Path(__file__).parent / "compiled_code.json"

with open(compiled_contract_json_path, "w") as file:
    json.dump(compiled_contract, file)

# Get data from compiled contract
compiled_data = compiled_contract["contracts"]["SimpleStorage.sol"]["SimpleStorage"]
bytecode = compiled_data["evm"]["bytecode"]["object"]
abi = compiled_data["abi"]

# Get data from ENV
http_provider_url = os.getenv("HTTP_PROVIDER_URL")
chain_id = int(os.getenv("CHAIN_ID"))
address = os.getenv("ADDRESS")
private_key = os.getenv("PRIVATE_KEY")

# Web3
w3 = Web3(Web3.HTTPProvider(http_provider_url))
simple_storage_contract = w3.eth.contract(abi=abi, bytecode=bytecode)
nonce = w3.eth.getTransactionCount(address)

# Build, sign and send contract deploy transaction
deploy_transaction = simple_storage_contract.constructor().buildTransaction(
    {
        "gasPrice": w3.eth.gas_price,
        "chainId": chain_id,
        "from": address,
        "nonce": nonce,
    }
)
signed_deploy_txn = w3.eth.account.sign_transaction(
    deploy_transaction, private_key=private_key
)
deploy_tx_hash = w3.eth.send_raw_transaction(signed_deploy_txn.rawTransaction)

# Working with deployed contract
deploy_tx_receipt = w3.eth.wait_for_transaction_receipt(deploy_tx_hash)
deployed_contract = w3.eth.contract(address=deploy_tx_receipt.contractAddress, abi=abi)

# Build, sign and send store transaction
store_transaction = deployed_contract.functions.store(15).buildTransaction(
    {
        "gasPrice": w3.eth.gas_price,
        "chainId": chain_id,
        "from": address,
        "nonce": nonce + 1,
    }
)
signed_store_txn = w3.eth.account.sign_transaction(
    store_transaction, private_key=private_key
)
send_store_tx = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
store_tx_receipt = w3.eth.wait_for_transaction_receipt(send_store_tx)

# Checking that previous transactions were sended
print(deployed_contract.functions.retrieve().call())

# ^^^
# Call - Simulate making the call and getting a return value
# Transact - Actually make a state change
