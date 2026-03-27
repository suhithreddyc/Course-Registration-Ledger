import time

def ts_to_str(unix_ts: int) -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(unix_ts))

def short_addr(addr: str) -> str:
    return f"{addr[:10]}...{addr[-6:]}" if len(addr) > 16 else addr

def extract_revert(err: str) -> str:
    """Pull the human-readable revert reason out of a Web3 exception."""
    triggers = [
        "Only admin can call this",
        "Wallet already registered",
        "Student ID already taken",
        "Student not registered",
        "Course not found",
        "Course is not active",
        "No seats available",
        "Already enrolled",
        "Max 4 courses reached",
        "Not enrolled in this course",
        "Registration not open yet",
        "Registration closed",
        "Cannot reduce below enrolled",
        "Course already exists",
    ]
    for t in triggers:
        if t in err:
            return t
    return "Transaction failed — check Ganache logs"