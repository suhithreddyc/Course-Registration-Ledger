import json, os, time
from web3 import Web3
from config import GANACHE_URL, CONTRACT_ADDRESS, ADMIN_ADDRESS, ADMIN_PRIVATE_KEY

w3 = Web3(Web3.HTTPProvider(GANACHE_URL))
if not w3.is_connected():
    raise ConnectionError(f"Cannot connect to Ganache at {GANACHE_URL}. Is it running?")

_base = os.path.dirname(__file__)
with open(os.path.join(_base, "contract_abi.json")) as f:
    ABI = json.load(f)

contract = w3.eth.contract(
    address=Web3.to_checksum_address(CONTRACT_ADDRESS),
    abi=ABI,
)

def _send_tx(fn, private_key: str, sender: str):
    sender  = Web3.to_checksum_address(sender)
    nonce   = w3.eth.get_transaction_count(sender)
    tx      = fn.build_transaction({
        "from":     sender,
        "nonce":    nonce,
        "gas":      400_000,
        "gasPrice": w3.to_wei("1", "gwei"),
    })
    signed  = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    return w3.eth.wait_for_transaction_receipt(tx_hash)

# ── Student ──────────────────────────────────────────────────────────────────
def register_student(student_id, wallet, private_key):
    return _send_tx(contract.functions.registerStudent(student_id), private_key, wallet)

def enroll_student(course_id, wallet, private_key):
    return _send_tx(contract.functions.enroll(course_id), private_key, wallet)

def drop_course(course_id, wallet, private_key):
    return _send_tx(contract.functions.drop(course_id), private_key, wallet)

def get_student_info(wallet):
    return contract.functions.getStudentInfo(Web3.to_checksum_address(wallet)).call()

# ── Courses ──────────────────────────────────────────────────────────────────
def get_all_courses():
    ids = contract.functions.getCourseIds().call()
    out = []
    for cid in ids:
        d = contract.functions.getCourse(cid).call()
        out.append({"id":d[0],"name":d[1],"total":d[2],
                    "enrolled":d[3],"available":d[4],"active":d[5]})
    return out

def is_enrolled(student_id, course_id):
    return contract.functions.isEnrolled(student_id, course_id).call()

# ── Ledger ───────────────────────────────────────────────────────────────────
def get_full_ledger():
    n = contract.functions.getLedgerLength().call()
    rows = []
    for i in range(n):
        e = contract.functions.getLedgerEntry(i).call()
        rows.append({
            "index": i,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(e[0])),
            "student_id": e[1],
            "course_id": e[2],
            "action": e[3],
            "success": "✅" if e[4] else "❌",
        })
    return rows

# ── Admin ────────────────────────────────────────────────────────────────────
def admin_update_seats(course_id, new_total):
    return _send_tx(contract.functions.updateSeats(course_id, new_total),
                    ADMIN_PRIVATE_KEY, ADMIN_ADDRESS)

def admin_toggle_course(course_id, active):
    return _send_tx(contract.functions.toggleCourse(course_id, active),
                    ADMIN_PRIVATE_KEY, ADMIN_ADDRESS)

def admin_add_course(course_id, name, seats):
    return _send_tx(contract.functions.addCourse(course_id, name, seats),
                    ADMIN_PRIVATE_KEY, ADMIN_ADDRESS)

def admin_set_window(start_ts, end_ts):
    return _send_tx(contract.functions.setRegistrationWindow(start_ts, end_ts),
                    ADMIN_PRIVATE_KEY, ADMIN_ADDRESS)

def get_registration_window():
    return contract.functions.getRegistrationWindow().call()

# ── Network ──────────────────────────────────────────────────────────────────
def get_ganache_accounts():
    return w3.eth.accounts

def get_balance(address):
    return float(w3.from_wei(w3.eth.get_balance(Web3.to_checksum_address(address)), "ether"))

def get_block_number():
    return w3.eth.block_number