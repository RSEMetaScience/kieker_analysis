"""Build the agent activity table used by the clustering notebook.

Run from the project root:  poetry run python -m kieker_analysis.stats.user_activity
"""
from pathlib import Path

import pandas as pd
from SPARQLWrapper import SPARQLWrapper

from kieker_analysis.sparql.client import kieker_client
from kieker_analysis.stats.pseudo import pseudonymise
from kieker_analysis.stats.agent_cleanup import clean_agents
from kieker_analysis.stats.contributor_metrics import (
    get_issue_event_counts,
    get_mentions_and_refs,
    get_user_activity,
    metrics_all,
)

# src/kieker_analysis/stats/user_activity.py -> parents[3] is the project root.
# Anchoring on __file__ means the output lands in the same place whether this is
# run from the root, a notebook, or PyCharm (the old script wrote to the cwd,
# which is how we ended up with two copies of the CSV).
DEFAULT_OUTPUT = Path(__file__).resolve().parents[3] / "results" / "user_activity.csv"


def merge_activity_tables(
    jira_events: pd.DataFrame,
    github_activity: pd.DataFrame,
    mentions_refs: pd.DataFrame,
) -> pd.DataFrame:
    """Outer-join the three per-agent tables on 'agent'.

    An agent missing from one table gets 0 for that table's columns.
    """
    merged = jira_events.merge(github_activity, on="agent", how="outer")
    merged = merged.merge(mentions_refs, on="agent", how="outer")
    return merged.fillna(0)


def build_user_activity(
    client: SPARQLWrapper = kieker_client,
    output: Path | None = DEFAULT_OUTPUT,
) -> pd.DataFrame:
    """Query the repo behind `client` and return one row per agent, one column per metric.

    Category merging (issue_link, dev_process, ...) is deliberately NOT done
    here; that stays in the notebook so it can be varied.
    Pass output=None to skip writing the CSV.
    """
    jira_events = get_issue_event_counts(client)

    github_activity = get_user_activity(metrics_all(client))
    # get_user_activity names its first column "agents"; everything else uses "agent".
    github_activity = github_activity.rename(columns={"agents": "agent"})
    # drop metrics nobody scored on (all-zero columns); keep 'agent' first
    nonzero = (github_activity.drop(columns="agent") != 0).any()
    github_activity = github_activity[["agent", *nonzero[nonzero].index]]

    mentions_refs = get_mentions_and_refs(client)

    # identity clean-up and anonymisation happens here, before saving, so the notebook never sees real logins
    merged = pseudonymise(clean_agents(merge_activity_tables(jira_events, github_activity, mentions_refs)))

    if output is not None:
        output = Path(output)
        output.parent.mkdir(parents=True, exist_ok=True)
        merged.to_csv(output, index=False)
    return merged


if __name__ == "__main__":
    table = build_user_activity()
    print(f"{len(table)} agents x {table.shape[1] - 1} metrics -> {DEFAULT_OUTPUT}")