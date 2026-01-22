from enum import Enum
from pathlib import Path


class Query(Enum):
    contributor_activity = "contributor_activity.sparql"
    named_issue = "named_issue.sparql"
    agents = "agents.sparql"
    issues_events = "issues_events.sparql"
    user_roles = "user_role_graph.sparql"
    timed_user_roles = "user_role_graph_T.sparql"
    pulls_commits_ct = "pulls_commits_ct.sparql"
    interactivity_variety = "interactivity_variety.sparql"

def _get_query_path(query:Query):
    return  Path(__file__).resolve().parent / query.value


def get_query(query:Query):
    query_path = _get_query_path(query)
    with open(query_path) as query:
        return query.read()

def get_parameterised_query(query:Query|str, args:list[tuple]|list[str], place_holder:str="{~{VALUES}~}") -> str:
    """get a query with placeholders replaced by a set of arguments
    :param query: supplies the sparql query filename
    :type query: Query enum
    :param args: a list of one or more arguments (tuples) e.g ("<url1>", "<url2>") or ("<url1>")
    :type args: list[tuple]
    :param place_holder: the place holder to replace arguments
    :type place_holder: str
    """
    query=get_query(query) if isinstance(query, Query) else query
    value_items = ''.join(f"{item}" for item in args)
    if place_holder not in query:
        raise ValueError("query does not accept arguments")
    for item in args:
        value_items.join(item)
    return query.replace(place_holder, value_items)

