from kieker_analysis.queries.queries import Query

query_strings = dict(
commits_started=Query.commits_started,
pull_reqs_opened=Query.pull_reqs_opened,
issues_opened=Query.issues_opened,
issue_comments=Query.issue_comments,
pullrequest_comments=Query.pullrequest_comments,
mention_issue_comments=Query.mention_issue_comments,
mention_pull_comments=Query.mention_pull_comments,
referred_issue_comments=Query.referred_issue_comments,
referred_pull_comments=Query.referred_pull_comments,
labels_issue=Query.labels_issue,
labels_pull=Query.labels_pull,
closed_issue=Query.closed_issue,
closed_pull=Query.closed_pull
)




def metrics_all():
    r={}
    for i, query in query_strings.items():
        t = results(query, i)
        r[i] = t[1]
    return r