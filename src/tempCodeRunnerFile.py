def fetch_civic_all_evidence_items():
    after_cursor = None
    all_items = []
    page = 1
    query = f"""
      {{
        evidenceItems(status: ACCEPTED, first: 500{f', after: "{after_cursor}"' if after_cursor else ''}) {{
          pageInfo {{
            hasNextPage
            endCursor
          }}
          nodes {{
            id
            significance
            evidenceDirection
            description
            molecularProfile {{
              name
            }}
            therapies {{
              name
            }}
            disease {{
              name
              diseaseAliases
            }}
          }}
        }}
      }}
      """
    
    
    

  
      # response = requests.post(GRAPHQL_URL, json={"query": query}, headers=HEADERS)
      # response.raise_for_status()
    data = help_request("https://civicdb.org/api/graphql", {"Content-Type": "application/json"}, query).json()["data"]["evidenceItems"]
    all_items.extend(data["nodes"])

    if not data["pageInfo"]["hasNextPage"]:
        data = None
    after_cursor = data["pageInfo"]["endCursor"]
    page += 1
    time.sleep(0.2)

    return all_items