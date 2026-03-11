from kieker_analysis.queries.queries import QueryOld
from kieker_analysis.sparql.client import run_dataframe
from pandas import DataFrame

from kieker_analysis.stats.util import min_max_normalise


def run_and_merge():
    df1 = run_dataframe(query=QueryOld.interactivity_variety)
    df2 = run_dataframe(query=QueryOld.pulls_commits_ct)
    merged = df1.merge(df2, on="agent", how="outer")
    metric_cols = ["interactivity", "variety", "pulls", "comments"]
    merged[metric_cols] = merged[metric_cols].fillna(0).astype("Int64")
    return min_max_normalise(merged,metric_cols)


