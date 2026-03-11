import numpy as np
import pandas as pd
from kieker_analysis.sparql.client import run


def min_max_normalise(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    out = df.copy()

    col_min = out[columns].min()
    col_max = out[columns].max()
    denom = (col_max - col_min).replace(0, np.nan)   # avoid divide-by-zero

    out[columns] = (out[columns] - col_min) / denom
    out[columns] = out[columns].fillna(0.0)          # constant columns -> 0.0

    return out


def results(query, metric, client = None)->tuple[str, dict]:
    """ run a sparql query for one of the metrics and return a tuple with the metric name and result (a dict with the
    value for each agent)
    :param query: a sparql query
    :type query: str
    :param metric: the name of the metric
    :type metric: str
    :param client: an instance of SPARQLWrapper
    :type client: SPARQLWrapper
    :return: a tuple of the form (metric_name, metric_values)
    :rtype: tuple
    """
    sparql_results = run(query, client)
    result_set = {}

    for result in sparql_results["results"]["bindings"]:
        agent_uri = result["agent"]["value"]
        count = int(result["count"]["value"])
        result_set[agent_uri]=count

    return metric, result_set





def _split_uri(uri:str)->str:
    parts = uri.split("#")
    if len(parts) == 2:
        return parts[1]
    else:
        parts = uri.split("/")
        return parts[-1]

def short_name(uri: str) -> str:
    slug = _split_uri(uri)
    for uri_prefix, namespace in [
        ("http://soton.ac.uk/pars#", "pars:"),
        ("https://github.com/", "github:"),
        ("http://purl.org/jira2prov/", "jira2prov:")]:

        if uri.startswith(uri_prefix):
            return f"{namespace}{slug}"

    return uri






def _split_uri(uri:str)->str:
    parts = uri.split("#")
    if len(parts) == 2:
        return parts[1]
    else:
        parts = uri.split("/")
        return parts[-1]
