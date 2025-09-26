
from asyncio import Runner
from typing import Any
from urllib import response
import requests
from requests.adapters import HTTPAdapter, Retry
import json
from graphql import GraphQLError
import logging


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
    return s.lower().replace("::", "-").replace("_", "-").strip()


def help_request(url: str, headers: dict, payload: dict = None, method: str = "GET") -> dict:
    

    try:
        resp = s.request(
        method=method,           # "GET" or "POST"
        url=url,
        headers=headers,
        json=payload if method == "POST" else None,
        timeout=(connect, read))
        if "application/json" not in resp.headers.get("Content-Type", ""):
            raise RuntimeError(f"Expected JSON but got {resp.headers.get('Content-Type')} from {url}")
        resp.raise_for_status()
        data = resp.json()
        



        return data 
    except requests.exceptions.Timeout:
        raise RuntimeError(f"Timeout after 10s for {url}")
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Request to {url} failed: {e}")
        
    except ValueError as e:
        raise RuntimeError(f"Invalid JSON in response from {url}: {e}")

def graphql_query(url: str, query: str, variables: dict | None = None, headers: dict | None = None) -> dict[str, Any]:
   
    # Runs a GraphQL query and enforces protocol semantics.
    # Returns only the 'data' field.
    # Raises GraphQLError if the response has errors or missing data.
    
    payload = {"query": query}
    if variables:
        payload["variables"] = variables

    response = help_request(url, headers, payload=payload, method="POST")

    if "errors" in response and response["errors"]:
        # extract first error message & path
        msg = response["errors"][0].get("message", "Unknown error")
        path = response["errors"][0].get("path")
        code = response["errors"].get("extensions", {}).get("code")
        logging.debug("GraphQL errors: %s",response["errors"])
        raise GraphQLError(f"{msg} (path={path}, code ={code})")
        

    if "data" not in response or response["data"] is None:
        logging.debug(response)
        raise GraphQLError("No data returned")
        
        

    return response["data"] 


    
    

        



    

