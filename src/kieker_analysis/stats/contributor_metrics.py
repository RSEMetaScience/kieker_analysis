import pandas as pd
from SPARQLWrapper import JSON


from kieker_analysis.queries.queries import Query, get_parameterised_query, get_query
from kieker_analysis.sparql.client import kieker_client, run, run_dataframe

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
def metric_factor_map()->dict:
    mapping = {}
    mapping['closed_issue'] = '# of times closed issues'
    mapping['closed_pull'] = '# of times closed pull requests'
    mapping['commits_started'] = '# of commits made'
    mapping['issue_comments'] = '# of comments made in issue discussions'
    mapping['issues_opened'] = '# of issues reported'
    mapping['labels_issue'] = '# of times applied or removed labels on issues'
    mapping['labels_pull'] = '# of times applied or removed labels on PRS'
    mapping['mention_issue_comments'] = '# of times being mentioned in issue comments'
    mapping['mention_pull_comments'] = '# of times being mentioned in PR comments'
    mapping['pr_comments'] = '# of comments made in PR discussions'
    mapping['pull_reqs_opened'] = '# of pull requests (PRs) made'
    mapping['referred_issue_comments'] = '# of times referred other issues/PRS in issue comments'
    mapping['referred_pull_comments'] = '# of times referred other issues/PRS in PR comments'
    return mapping


def results(query, metric)->tuple[str, dict]:
    """ run a sparql query for one of the metrics and return a tuple with the metric name and result (a dict with the
    value for each agent)
    :param query: a sparql query
    :type query: str
    :param metric: the name of the metric
    :type metric: str
    :return: a tuple of the form (metric_name, metric_values)
    :rtype: tuple
    """
    sparql_results = run(query)
    result_set = {}

    for result in sparql_results["results"]["bindings"]:
        agent_uri = result["agent"]["value"]
        count = int(result["count"]["value"])
        result_set[agent_uri]=count

    return metric, result_set


def metrics_all()->dict:
    r={}
    for i, query in query_strings.items():
        t = results(query, i)
        r[i] = t[1]
    return r

def build_weights()->pd.DataFrame:
    """use the factor loadings table from Cheng and Guo, 'Activity-based analysis of open source software contributors:
    Roles and dynamics' (10.1109/CHASE.2019.00011) to provide the weightings we need to compute the factors from that
    paper using our results """
    weights_raw=[
        ["Metrics", "# of commits made", "# of line of code changed in the codebase", "# of files worked on", "# of pull requests (PRs) made", "Avg. length of PR descriptions", "# of issues reported", "Avg. length of issue descriptions", "# of comments made in issue discussions", "Avg. length of issue comments", "# of comments made in PR discussions", "Avg.  length of PR comments", "# of times being mentioned in issue comments", "# of times being mentioned in PR comments", "# of times referred other issues/PRS in issue comments", "# of times referred other issues/PRS in PR comments", "# of times applied or removed labels on issues", "# of times applied or removed labels on PRS", "# of times closed issues", "# of times closed pull requests" , "Activity Name"],
        ["Factor1", 0.00,0.00,0.00,0.06,0.05,0.30,-0.01,0.52,-0.02,0.72,0.00,0.78,1.02,-0.12,0.06,0.06,0.58,0.28,-0.30 , "Knowledge. Sharing"],
        ["Factor2", 1.03,1.03,0.26,-0.04,-0.01,0.04,0.00,-0.01,0.01,-0.01,-0.01,0.01,0.01,0.02,0.00,0.01,0.00,-0.03,-0.08 , "Code Contrib"],
        ["Factor3", 0.02,0.02,-0.07,-0.11,-0.03,0.18,-0.03,0.30,0.00,0.09,0.04,0.1,-0.16,1.06,0.59,0.72,0.13,0.08,0.07, "Issue Coord"],
        ["Factor4", -0.07,-0.07,0.35,0.45,-0.01,0.11,0.00,0.24,-0.01,0.03,-0.02,0.01,-0.2,-0.07,-0.05,0.24,-0.03,0.65,0.95 , "Prog.  Ctrl."],
        ["Factor5", -0.04,-0.04,0.45,0.70,0.13,0.11,0.02,-0.13,0.00,0.25,0.09,-0.02,0.2,0.02,0.21,-0.23,0.15,-0.24,0.33 , "Code Twking."],
        ["Factor6", 0.05,0.05,-0.17,0.05,0.01,0.35,0.16,0.16,0.1,-0.12,0.03,0.14,-0.22,-0.15,0.00,-0.07,-0.07,0.04,-0.06 , "Issue Rptg."],
        ["h2", 0.997,0.997,0.575,0.876,0.022,0.643,0.024,0.900,0.008,0.820,0.013,0.840,0.743,0.808,0.503,0.725,0.516,0.701,0.857, ""],
        ["u2", 0.003,0.003,0.425,0.124,0.978,0.358,0.976,0.100,0.992,0.180,0.987,0.160,0.257,0.192,0.497,0.275,0.485,0.299,0.144, ""]
    ]

    transpose=list(zip(*weights_raw))
    rows = [x[0] for x in transpose]
    columns = transpose[-1][1:7] + transpose[0][-2:]
    weights_data = [x[1:] for x in transpose[1:-1]]
    return pd.DataFrame(weights_data, columns=columns, index=[x[0] for x in transpose][1:-1])

def get_active_users(metrics:dict)->set[str]:
    users = set()
    for analysis in metrics.values():
        for u in analysis.keys():
            users.add(u)
    return users

def get_kieker_event_count(users_to_drop:list[str]|None=None)->pd.DataFrame:
    argz=[]
    if users_to_drop:
        arg = ''",".join(f"{v}" for v in users_to_drop)
        argz.append(arg)
    q_string=get_query(Query.kieker_event_count)
    q=get_parameterised_query(q_string,argz)
    df=run_dataframe(q)
    df = df[df['event_type']!="http://www.w3.org/ns/prov#Activity"]
    return df

def get_user_activity(metrics:dict)->pd.DataFrame:
    users = get_active_users(metrics)
    columns = sorted(metrics.keys())
    data = []
    short_users = []
    for u in users:
        d = [metrics[x].get(u, 0) for x in columns]
        data.append(d)
        un = u.replace("https://api.github.com/users/", "")
        short_users.append(un)

    user_activity = pd.DataFrame(data, columns=columns, index=short_users)
    return user_activity

def get_all_user_metrics(users_to_drop:list[str]|None=None):
    argz = []
    if users_to_drop:
        arg = ''",".join(f"{v}" for v in users_to_drop)
        argz.append(arg)
    q_string = get_query(Query.all_agent_activity)
    q = get_parameterised_query(q_string, argz)
    df = run_dataframe(q)
    df_wide= (
            df.pivot_table(index="agent",
                            columns="event_type_short",
                            values="events",
                            aggfunc="sum",
                            fill_value=0).reset_index()
)

    df_wide.drop(columns=["Activity"], inplace=True)
    return df_wide