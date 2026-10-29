from collections import defaultdict

import pandas as pd

from kieker_analysis.queries.queries import Query

from kieker_analysis.sparql.client import kieker_client, jira_patch_client
from kieker_analysis.stats.contributor_metrics import metrics_all, get_user_activity, get_issue_event_counts, \
    get_mentions_and_refs  # , build_weights, get_kieker_event_count


if __name__ == '__main__':
    # metrics_all = metrics_all()
    # user_activity = get_user_activity(metrics_all)
    # print(user_activity)
    # dropped_users = ['users:rju']
    # get_kieker_event_count(dropped_users)

    # dupes = defaultdict(list)
    # client = jira_patch_client
    # # metrics_all = metrics_all(client)
    # # user_activity = get_user_activity(metrics_all)
    # query=Query.jira_issue_events.value
    # jira_events = get_issue_event_counts(client)
    # jira_events.rename(columns={jira_events.columns[0]: "agent"}, inplace=True)
    # metrics_all = metrics_all(client)
    # user_activity = get_user_activity(metrics_all)
    # refs_mentions=get_mentions_and_refs(client)
    # # drop the columns with only zeros
    # user_activity = user_activity.loc[:, (user_activity != 0).any()]
    # user_activity.rename(columns={user_activity.columns[0]: "agent"}, inplace=True)
    # merged = jira_events.merge(user_activity, on="agent", how="outer")
    # merged=merged.merge(refs_mentions, on="agent", how="outer")
    # merged = merged.fillna(0)
    # merged.to_csv("user_activity_merged.csv", index=False)

    # for column in jira_events.columns:
    #     key = tuple(jira_events[column].tolist())
    #     dupes[key].append(column)
    # dupes = [cols for cols in dupes.values() if len(cols)>1]
    # for group in dupes:
    #     print("These are indentical:")
    #     for item in group:
    #         print(f"- {item}")
    #     print(f"********* \n")

    results = pd.read_csv("user_activity_merged.csv", index_col='agent')
    results["total"] = results.sum(axis=1)
    issue_link = ["jira2prov:Parent", "jira2prov:ParentIssue", "jira2prov:ParentIssue", "jira2prov:Link",
                  "jira2prov:ExternalissueID", "jira2prov:RemoteIssueLink"]
    issue_progress = ["jira2prov:status", "jira2prov:Workflow", "jira2prov:resolution"]
    categorising = ["jira2prov:labels", "jira2prov:priority", "jira2prov:issuetype"]
    dev_process = ["jira2prov:FixVersion", "jira2prov:Version", "jira2prov:Component", "jira2prov:Milestone",
                   "jira2prov:Sprint"]
    issue_content = ["jira2prov:description", "jira2prov:Attachment", "jira2prov:summary"]
    comment_activity = ["jira2prov:comment", "jira2prov:Comment"]
    merges = {"issue_link": issue_link, "issue_progress": issue_progress, "categorising": categorising,
              "dev_process": dev_process, "issue_content": issue_content, "comment_activity": comment_activity}

    for merge in merges:
        results[merge] = results[merges[merge]].sum(axis=1)
        merged_results = results.drop(columns=merges[merge], inplace=False)
    merged_results


    a="a"