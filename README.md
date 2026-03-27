# Course Registration Ledger (Blockchain)

A smart-contract-based course registration system built with Ethereum, Brownie, and Python.
Students and instructors register courses on-chain with transparent course ledger state.

## 🔧 Project Structure

- pp/
  - pp.py: Flask or CLI app interface (blockchain interaction endpoint)
  - config.py: config constants (network, account, contract address)
  - contract_interface.py: wrapper for deployed contract methods
  - deployment.json: deployment details for a network
  - utils.py: helper functions
  - contract_abi.json: ABI for /contracts/CourseRegistration.sol contract

- lockchain/
  - CourseRegistration.sol: Solidity smart contract source (core logic)

- contracts/
  - CourseRegistration.sol: copy used by some Brownie workflows

- uild/
  - contracts/CourseRegistration.json: compiled ABI + bytecode
  - deployments/...: contract address history for networks

- interfaces/
  - (optional interface definitions)

- eports/
  - (test coverage / gas reports)

- scripts/
  - deploy.py: deployment script for local chain

- 	ests/
  - tests for smart contract and app logic

- rownie-config.yaml: Brownie project settings
- equirements.txt: Python dependencies
- README.md: this file

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.10+ (or compatible)
- 
ode + 
pm (for Ganache/Hardhat if needed)
- Brownie (pip install eth-brownie)
- Ganache local chain (e.g. 
pm install -g ganache-cli) or Hardhat node

### 2. Setup

`ash
git clone <repo-url>
cd courseRegistrationLedger
python -m venv .venv
.venv\Scripts\activate     # Windows
# source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
brownie networks list      # verify local network config
`

### 3. Deploy

`ash
brownie run scripts/deploy.py --network development
`

- Deployed contract address is recorded in uild/deployments/1337/
- pp/deployment.json is updated with the latest address (from Brownie)

### 4. Run App

`ash
python app/app.py
`

or run CLI / test calls as supported by your app interface.

## 🧩 Smart Contract Details

### CourseRegistration.sol (core features)

- Add courses
- Register students
- Enroll/unenroll
- Query courses & students
- Audit trail on-chain

## 🧪 Tests

`ash
brownie test
`

- Tests should be located under 	ests/
- Includes unit coverage for contract functions and app integration

## 🛠️ Project Workflow

1. Update smart contract in lockchain/CourseRegistration.sol and contracts/CourseRegistration.sol
2. Recompile:
   - rownie compile
3. Rerun deploy script:
   - rownie run scripts/deploy.py --network development
4. Run app/tests.

## 📁 Notes

- If using Brownie local chain, use ganache-cli --deterministic --port 8545.
- Replace account index or mnemonic in rownie-config.yaml or pp/config.py as needed.
- Add additional UI or API layers on top of pp/contract_interface.py.

## 📝 Troubleshooting

- rownie.exceptions.NetworkError: run ganache first.
- ContractNotFound: verify uild/contracts/CourseRegistration.json exists and deployment address is correct.

## 📜 License

MIT License (or your desired license)
