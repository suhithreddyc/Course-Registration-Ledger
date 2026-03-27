import json
import os
from brownie import CourseRegistration, accounts, network, config

def main():
    print("=" * 55)
    print("  Course Registration Ledger — Deploying via Brownie")
    print("=" * 55)

    # accounts[0] is automatically Account[0] from Ganache
    deployer = accounts[0]

    print(f"\n  Admin (deployer) : {deployer.address}")
    print(f"  Balance          : {deployer.balance() / 1e18:.4f} ETH")

    print("\n  All Ganache accounts:")
    print("  " + "-" * 51)
    for i, acc in enumerate(accounts):
        bal = acc.balance() / 1e18
        print(f"  Account[{i}]: {acc.address}  ({bal:.2f} ETH)")
    print("  " + "-" * 51)

    print("\n  Deploying contract...")
    contract = CourseRegistration.deploy({"from": deployer})

    print(f"\n  Contract deployed at : {contract.address}")

    # Write deployment info + ABI into app/
    out_dir = os.path.join(os.path.dirname(__file__), "..", "app")
    os.makedirs(out_dir, exist_ok=True)

    deployment = {
        "contractAddress": contract.address,
        "adminAddress":    deployer.address,
        "network":         "ganache-local",
    }
    with open(os.path.join(out_dir, "deployment.json"), "w") as f:
        json.dump(deployment, f, indent=2)

    abi = contract.abi
    with open(os.path.join(out_dir, "contract_abi.json"), "w") as f:
        json.dump(abi, f, indent=2)

    print("  ABI written        → app/contract_abi.json")
    print("  Deployment info    → app/deployment.json")
    print("\n  NEXT: Open Ganache → click 🔑 next to Account[0]")
    print("        Copy the private key → paste into app/config.py")
    print("=" * 55)