import time
from utils import graphql_query
import logging

GRAPHQL_URL = "https://civicdb.org/api/graphql"
HEADERS = {"Content-Type": "application/json"}
API_THROTTLE = 0.2

log = logging.getLogger(__name__)


def fetch_civic_all_evidence_items():
    after_cursor = None
    all_items = []
    seen_ids = set()
    page = 1
    MAX_PAGES = 10000

    query = """
      query ($first: Int!, $after: String) {
        evidenceItems(status: ACCEPTED, first: $first, after: $after) {
          pageInfo {
            hasNextPage
            endCursor
          }
          nodes {
            id
            status
            significance
            evidenceType
            evidenceLevel
            evidenceRating
            evidenceDirection
            description
            molecularProfile { id name variants {
              name
              ... on GeneVariant { alleleRegistryId }
              feature { name } }}
            therapies { name ncitId }
            disease {doid name diseaseAliases }
            source { ascoAbstractId citationId pmcId sourceType title publicationYear }
          }
        }
      }
    """

    while True:
        data = graphql_query(
            url=GRAPHQL_URL,
            query=query,
            variables={"first": 500, "after": after_cursor},
            headers=HEADERS,
        )

        evidence_items = data["evidenceItems"]
        for node in evidence_items["nodes"]:
            if node["id"] not in seen_ids:
                seen_ids.add(node["id"])
                all_items.append(node)

        if not evidence_items["pageInfo"]["hasNextPage"]:
            break

        after_cursor = evidence_items["pageInfo"]["endCursor"]
        page += 1
        logging.info("Fetched page %s with %s items", page, len(all_items))
        time.sleep(API_THROTTLE)

        if page > MAX_PAGES:
            raise RuntimeError("Exceeded max pages — likely stuck in a loop")

    return all_items
