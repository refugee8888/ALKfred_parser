

def normalize(s: str) -> str:
    #defining what normalizing should do
    return s.lower().replace("::", "-").replace("_", "-").replace("fusion", "").strip()
