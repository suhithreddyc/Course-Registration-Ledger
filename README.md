# Course Registration Ledger

A decentralized course registration system on Ethereum. Admins manage courses and seat caps; students register wallets, enroll in courses (up to four), and drop—with state and an on-chain activity ledger stored in a Solidity contract. The UI is a **Streamlit** app that talks to the chain through **Web3**; **Brownie** compiles and deploys the contract.

## Tech stack

| Layer | Technology |
|--------|------------|
| Smart contract | Solidity 0.8.19 (`contracts/CourseRegistration.sol`) |
| Toolkit | [Brownie](https://eth-brownie.readthedocs.io/) (compile, deploy, accounts) |
| Local chain | [Ganache](https://trufflesuite.com/ganache/) (RPC on port **7545**, chain id **1337**—matches `app/config.py`) |
| Frontend | Streamlit (`app/app.py`) |
| Python | 3.10+ recommended |

## Repository layout

```
courseRegistrationLedger/
├── app/
│   ├── app.py              # Streamlit UI
│   ├── config.py           # RPC URL, contract address, admin key (set after Ganache + deploy)
│   ├── contract_interface.py # Web3 wrappers for the contract
│   ├── utils.py            # Helpers (e.g. short address formatting)
│   ├── deployment.json     # Written by deploy script (contract + admin addresses)
│   └── contract_abi.json   # Written by deploy script
├── contracts/
│   └── CourseRegistration.sol  # Brownie contract source
├── scripts/
│   └── deploy.py           # Deploys CourseRegistration; updates app/*.json
├── build/                  # Brownie compile & deployment artifacts
├── brownie-config.yaml     # Default network: ganache-local
├── ganache-db/             # Optional: persistent Ganache data (if you use local DB flags)
└── requirements.txt
```

## Prerequisites

- **Python** 3.10 or newer  
- **Ganache** (GUI or CLI) listening on **http://127.0.0.1:7545** with chain id **1337**  
  - Ganache Desktop defaults to port `7545`; if you use `ganache-cli`, set port `7545` or change `GANACHE_URL` in `app/config.py` to match.  
- **Git** (to clone the repo)

---

## Setup and run

Run all terminal commands from the **project root** (the folder that contains `brownie-config.yaml`).  
If Brownie warns that the loaded project root differs from your current working directory, `cd` into this folder before running `brownie` or `streamlit`.

### 1. Create a virtual environment

```bash
python -m venv venv
```

Activate it:

**Windows (cmd):**

```bat
venv\Scripts\activate
```

**Windows (PowerShell):**

```powershell
.\venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Start Ganache

Start Ganache so it exposes **JSON-RPC** at **127.0.0.1:7545** with **network id / chain id 1337**. Keep it running while you deploy and use the app.

### 4. Register the Brownie network

This adds an RPC network named `ganache-local` (same id as in `brownie-config.yaml`). The first argument is the Brownie environment name (`Ethereum`); the second is the network id.

```bash
brownie networks add Ethereum ganache-local host=http://127.0.0.1:7545 chainid=1337
```

If you already added this network, Brownie will report that it exists; you can skip this step or use `brownie networks list` to verify.

### 5. Compile and deploy the contract

```bash
brownie compile
brownie run scripts/deploy.py
```

With `brownie-config.yaml` as written, the default network is `ganache-local`, so you do not need `--network` unless you switch defaults.

The script will:

- Deploy `CourseRegistration` using Ganache **Account 0** as the contract admin  
- Write **`app/deployment.json`** (contract address, admin address)  
- Write **`app/contract_abi.json`**

### 6. Configure the admin private key (Streamlit)

The Streamlit app signs **admin-only** transactions (e.g. add course, change seats). That uses the same account that deployed the contract (Ganache Account 0).

1. Open Ganache and copy the **private key** for **Account 0** (key icon in the UI).  
2. Open **`app/config.py`** and set:

```python
ADMIN_PRIVATE_KEY = "0xPasteYourCopiedKeyHere"
```

Use the `0x` prefix. **Do not commit real private keys to Git.** For coursework, prefer environment variables or a local-only config if you extend the project.

`GANACHE_URL` in `config.py` must stay in sync with your Ganache port (default **7545**).

### 7. Run the Streamlit app

```bash
cd app
streamlit run app.py
```

Open the URL shown in the terminal (usually [http://localhost:8501](http://localhost:8501)).

---

## Contract overview (`CourseRegistration.sol`)

- **Admin** (deployer): add courses, update seat totals, toggle courses, set registration time window.  
- **Students**: register a student ID bound to their wallet, enroll/drop courses, respect max **4** courses per student (enforced on-chain).  
- **On-chain ledger**: append-only style records for enroll/drop and related actions.  
- Constructor seeds several default courses (e.g. Cloud Computing, Blockchain, etc.).

---

## Brownie notes

- **Working directory:** Always run `brownie` from the project root so scripts and imports resolve correctly (especially on Windows).  
- **Networks:** Default network is set in `brownie-config.yaml` (`ganache-local`).  
- **Redeploy:** Run `brownie run scripts/deploy.py` again; then refresh `ADMIN_PRIVATE_KEY` if Account 0 changed (e.g. new Ganache workspace).

---

## Troubleshooting

| Issue | What to check |
|--------|----------------|
| `NetworkError` / cannot connect | Ganache is running; URL/port matches `7545`; Brownie network `ganache-local` points at the same URL. |
| `ModuleNotFoundError: No module named 'deploy'` | Current directory is not the project root; `cd` to the repo root and retry. |
| App fails on import (`deployment.json` missing) | Run the deploy script once so `app/deployment.json` exists. |
| Transactions revert as admin | `ADMIN_PRIVATE_KEY` in `config.py` must be Account 0’s key (the deployer/admin). |
| Unicode/console errors on Windows when running Brownie | Set `PYTHONIOENCODING=utf-8` or use a terminal with UTF-8 output. |

---

## License

Specify your license here (e.g. MIT).
