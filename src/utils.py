import requests
from requests.adapters import HTTPAdapter, Retry
import json

s = requests.Session()

retries = Retry(total=5,
            backoff_factor=1,
            status_forcelist=[ 429, 500, 502, 503, 504 ], allowed_methods={"GET","POST"},
            respect_retry_after_header=True)

connect,read = 10,20
s.mount('https://', HTTPAdapter(max_retries=retries))
s.mount('http://', HTTPAdapter(max_retries=retries))



def normalize(s: str) -> str:
    #defining what normalizing should do
    return s.lower().replace("::", "-").replace("_", "-").replace("fusion", "").strip()

def help_request(url: str, headers: dict, payload: dict = None, method: str = "GET") -> dict:
    
                    

                
    try:
        resp = s.request(
        method=method,           # "GET" or "POST"
        url=url,
        headers=headers,
        json=payload if method == "POST" else None,
        timeout=(5, 20))
        resp.raise_for_status()
       
        return resp.json()
    except requests.exceptions.Timeout:
        raise RuntimeError(f"Timeout after 10s for {url}")
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Request to {url} failed: {e}")
        



    

