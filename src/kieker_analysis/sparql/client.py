from SPARQLWrapper import SPARQLWrapper, JSON, CSV, TURTLE
from io import StringIO


from rdflib import Graph

from kieker_analysis.queries.queries import Query, get_query
import pandas as pd

# kieker_client = SPARQLWrapper("http://localhost:3030/kieker/query")
kieker_client = SPARQLWrapper("http://localhost:7200/repositories/kieker")
keiker_ii_client = SPARQLWrapper("http://localhost:7200/repositories/kieker_ii")
def run(query:Query|str, client:SPARQLWrapper=kieker_client, result_format=JSON) -> bytes | str | dict :
    client = client
    query_string = get_query(query) if isinstance(query, Query) else query
    client.setQuery(query_string)
    client.setReturnFormat(result_format)
    return client.query().convert()

def run_dataframe(query:Query|str, client:SPARQLWrapper=kieker_client)->pd.DataFrame:
    """run a select query and put the results in a dataframe"""
    result=run(query=query, client=client, result_format=CSV).decode('utf-8')
    df = pd.read_csv(StringIO(result))
    df = df.map(lambda x: x.strip() if isinstance(x, str) else x)
    return df

def run_graph(query:str, client: SPARQLWrapper=kieker_client)-> Graph:
    """run a construct query for an RDFlib graph"""
    client=client
    if 'construct' not in query.lower():
        raise ValueError("this does not appear to be a construct query")
    client.setQuery(query)
    result = client.queryAndConvert()
    graph_has_nodes = len(result.all_nodes()) > 0
    if graph_has_nodes:
        return result
    raise ValueError("this query appears to have returned no results")

