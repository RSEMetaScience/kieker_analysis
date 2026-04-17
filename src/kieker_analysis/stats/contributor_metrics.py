import pandas as pd
from SPARQLWrapper import SPARQLWrapper

from kieker_analysis.queries.queries import Query
from kieker_analysis.sparql.client import run_dataframe
from kieker_analysis.stats.util import results, short_name

query_strings = dict(
    commits_started=Query.commits_started,
    pull_reqs_opened=Query.pull_reqs_opened,
    issues_opened=Query.issues_opened,
    issue_comments=Query.issue_comments,
    pr_comments=Query.pr_comments,
    mention_issue_comments=Query.mention_issue_comments,
    mention_pull_comments=Query.mention_pull_comments,
    referred_issue_comments=Query.referred_issue_comments,
    referred_pull_comments=Query.referred_pull_comments,
    labels_issue=Query.labels_issue,
    labels_pull=Query.labels_pull,
    closed_issue=Query.closed_issue,
    closed_pull=Query.closed_pull
)


def metrics_all(client: SPARQLWrapper) -> dict:
    r = {}
    for i, query in query_strings.items():
        t = results(query, i, client)
        r[i] = t[1]
    return r


def get_mentions_and_refs(client: SPARQLWrapper) -> pd.DataFrame:
    refs = run_dataframe(query=Query.jira_agent_refs_issues, client=client)
    agent_mentions = run_dataframe(query=Query.jira_agent_mentions_others, client=client)
    agent_mentioned = run_dataframe(query=Query.jira_agent_is_mentioned, client=client)
    results=agent_mentioned.merge(agent_mentions, on='agent',how='outer')
    results=results.merge(refs, on='agent', how='outer')
    results['agent'] = results['agent'].apply(short_name)
    return results.fillna(0)


def get_issue_event_counts(client: SPARQLWrapper) -> pd.DataFrame:
    query = Query.jira_issue_events
    result: pd.DataFrame() = run_dataframe(query=query, client=client)
    result['agent'] = result['agent'].apply(short_name)
    pvt = pd.pivot_table(result, values='count',
                         index='agent', columns='e_type',
                         aggfunc="sum", fill_value=0)
    pvt.columns = pvt.columns.map(short_name)
    pvt = pvt.reset_index()
    pvt.columns.name = None
    pvt.index.name = None
    return pvt


def get_user_activity(metrics: dict) -> pd.DataFrame:
    users = get_active_users(metrics)
    columns = sorted(metrics.keys())
    data = []
    short_users = []
    for user in users:
        d = [metrics[x].get(user, 0) for x in columns]
        data.append(d)
        # user_id = _split_uri(user)
        user_id = short_name(user)
        short_users.append(user_id)

    user_activity = pd.DataFrame(data, columns=columns)
    user_activity.insert(0, "agents", short_users)
    return user_activity


def get_active_users(metrics: dict) -> set[str]:
    users = set()
    for analysis in metrics.values():
        for u in analysis.keys():
            users.add(u)
    return users
