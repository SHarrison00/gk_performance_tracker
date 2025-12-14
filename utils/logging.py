from datetime import datetime 

def ts():
    return datetime.now().isoformat(timespec="seconds")
