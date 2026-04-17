from enum import Enum
from pathlib import Path


class QueryOld(Enum):
    contributor_activity = "contributor_activity.sparql"
    named_issue = "named_issue.sparql"
    agents = "agents.sparql"
    issues_events = "issues_events.sparql"
    user_roles = "user_role_graph.sparql"
    timed_user_roles = "user_role_graph_T.sparql"
    pulls_commits_ct = "pulls_commits_ct.sparql"
    interactivity_variety = "metrics/interactivity_variety.sparql"
    counts = "counts.sparql"
    pull_reqs_opened = "metrics/pull_reqs_opened.sparql"
    issues_opened = "metrics/issues_opened.sparql"
    pr_comments = "metrics/pr_comments.sparql"
    closed_pull="metrics/closed_pull.sparql"
    closed_issue="metrics/closed_issue.sparql"
    labels_pull = "metrics/labels_pull.sparql"
    referred_pull_comments = "metrics/refd_pull_comments.sparql"
    referred_issue_comments = "metrics/refd_issue_comments.sparql"
    mention_pull_comments   = "metrics/mention_pull_comments.sparql"
    mention_issue_comments = "metrics/mention_issue_comments.sparql"
    commits_started = "metrics/commits_started.sparql"
    issue_comments = "metrics/issue_comments.sparql"
    labels_issue = "metrics/labels_issue.sparql"
    kieker_event_count = "kieker_event_count.sparql"
    all_agent_activity = "all_agent_activity.sparql"

class Query(Enum):
    jira_agent_refs_issues = "jira_Patch/metrics/agent_refs_issues.sparql"
    jira_agent_mentions_others = "jira_patch/metrics/agent_mentions_others.sparql"
    jira_agent_is_mentioned = "jira_patch/metrics/agent_is_mentioned.sparql"
    jira_issue_events = "jira_patch/metrics_all.sparql"
    contributor_activity = "jira_patch/contributor_activity.sparql"
    named_issue = "named_issue.sparql"
    agents = "agents.sparql"
    issues_events = "issues_events.sparql"
    user_roles = "user_role_graph.sparql"
    timed_user_roles = "user_role_graph_T.sparql"
    pulls_commits_ct = "pulls_commits_ct.sparql"
    interactivity_variety = "metrics/interactivity_variety.sparql"
    counts = "counts.sparql"
    pull_reqs_opened = "jira_patch/metrics/pull_reqs_opened.sparql"
    issues_opened = "jira_patch/metrics/issues_opened.sparql"
    pr_comments = "metrics/pr_comments.sparql"
    closed_pull="jira_patch/metrics/closed_pull.sparql"
    closed_issue="jira_patch/metrics/closed_issue.sparql"
    labels_pull = "jira_patch/metrics/labels_pull.sparql"
    referred_pull_comments = "metrics/refd_pull_comments.sparql"
    referred_issue_comments = "metrics/refd_issue_comments.sparql"
    mention_pull_comments   = "metrics/mention_pull_comments.sparql"
    mention_issue_comments = "metrics/mention_issue_comments.sparql"
    commits_started = "jira_patch/metrics/commits_started.sparql"
    issue_comments = "jira_patch/metrics/issue_comments.sparql"
    labels_issue = "metrics/labels_issue.sparql"
    kieker_event_count = "kieker_event_count.sparql"
    all_agent_activity = "all_agent_activity.sparql"





def _get_query_path(query:QueryOld|Query):
    return  Path(__file__).resolve().parent / query.value


def get_query(query:QueryOld):
    query_path = _get_query_path(query)
    with open(query_path) as query:
        return query.read()

def get_parameterised_query(query: QueryOld | str, args: list[tuple] | list[str], place_holder:str= "{~{VALUES}~}") -> str:
    """get a query with placeholders replaced by a set of arguments
    :param query: supplies the sparql query filename
    :type query: Query enum
    :param args: a list of one or more arguments (tuples) e.g ("<url1>", "<url2>") or ("<url1>")
    :type args: list[tuple]
    :param place_holder: the place holder to replace arguments
    :type place_holder: str
    """
    query=get_query(query) if isinstance(query, QueryOld) else query
    value_items = ','.join(f"{item}" for item in args)
    if place_holder not in query:
        raise ValueError("query does not accept arguments")
    for item in args:
        value_items.join(item)
    return query.replace(place_holder, value_items)

