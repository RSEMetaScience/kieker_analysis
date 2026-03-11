import rdflib.term
from rdflib import Graph as rdfGraph
from rdflib.namespace import RDF
from rdflib import Literal

from kieker_analysis.graph.cyto_styles import usr_role_styler
from kieker_analysis.graph.layouts.util import truncate_last_path, prettify_predicate
from kieker_analysis.queries.queries import get_parameterised_query, QueryOld
from kieker_analysis.sparql.client import run_graph
import networkx as nx

extra_types=[rdflib.term.URIRef("http://purl.org/github2prov/comment"),
                rdflib.term.URIRef("http://purl.org/github2prov/commit"),
                rdflib.term.URIRef("http://purl.org/github2prov/closed"),
                rdflib.term.URIRef("http://purl.org/github2prov/created"),
                rdflib.term.URIRef("http://purl.org/github2prov/assigned"),
                rdflib.term.URIRef("http://purl.org/github2prov/labeled"),
                rdflib.term.URIRef("http://purl.org/github2prov/merged"),
                rdflib.term.URIRef("http://purl.org/github2prov/renamed"),
                rdflib.term.URIRef("http://purl.org/github2prov/head_ref_deleted"),
                rdflib.term.URIRef("http://purl.org/github2prov/review_requested"),
                rdflib.term.URIRef("http://purl.org/github2prov/referenced"),
                rdflib.term.URIRef("http://purl.org/github2prov/pull_request_review"),
                rdflib.term.URIRef("http://purl.org/github2prov/review_request_removed"),
                rdflib.term.URIRef("http://purl.org/github2prov/base_ref_changed"),
                rdflib.term.URIRef("http://purl.org/github2prov/reopened"),
                rdflib.term.URIRef("http://purl.org/github2prov/head_ref_restored")

             ]

def render():
    pass


def issue_graph(issue:str):
    query = get_parameterised_query(QueryOld.named_issue, [f"<{issue}>"])
    rdf_graph=run_graph(query)
    return rdflib_to_networkx(rdf_graph, rdf_types=extra_types)

def user_role_graph(user:str):
    query=get_parameterised_query(QueryOld.user_roles, [f"github:{user}"])
    rdf_graph=run_graph(query)
    nx_graph = rdflib_to_networkx(rdf_graph, rdf_types=extra_types)
    add_formatting_styles(nx_graph,usr_role_styler)
    return nx_graph

def timed_user_role_graph(user:str, step=2, iters=5):
    query=get_parameterised_query(QueryOld.timed_user_roles, [f"github:{user}"])
    increment=2
    for _ in range(iters):
        timed_query = get_parameterised_query(query,[f"{increment}"],place_holder="{~{DURATION}~}")
        try:
            rdf_graph=run_graph(timed_query)
        except ValueError:
            rdf_graph=get_the_graph_that_time_forgot()
        nx_graph = rdflib_to_networkx(rdf_graph, rdf_types=extra_types)
        add_formatting_styles(nx_graph,usr_role_styler)
        yield nx_graph
        increment+=step

def rdflib_to_networkx(rdf_graph: rdfGraph, rdf_types:list[str]=None, labels:bool=True) -> nx.DiGraph:
    """
    convert an rdflib Graph (rdfGraph) into a NetworkX DiGraph.

    - subjects and objects become nodes
    - predicates become edge attributes
    """
    nx_graph = nx.DiGraph()
    if rdf_types is None:
        rdf_types = []
    for subject, predicate, _object in rdf_graph:
        nx_graph.add_node(subject)

        # For rdf:type triples  make them literals, ie, add a string literal here and loop to the next triple
        if predicate == RDF.type and _object not in rdf_types:
            nx_graph.nodes[subject].setdefault(
                "rdf_type", set()
            ).add(str(_object))
            continue
        # skip labels
        if isinstance(_object, Literal):
            continue

        nx_graph.add_node(_object)
        nx_graph.add_edge(
            subject,
            _object,
            predicate=str(predicate)
        )

    if labels:
        add_visual_labels(nx_graph,True, True, True)

    return nx_graph

def add_visual_labels(nx_graph: nx.DiGraph,
                      trunc=False,
                      short_predicates=False,
                      b_nodes=False) -> nx.DiGraph:
    """
    Add human-readable labels to nodes and edges for visualisation.
    """
    # node labels
    for node in nx_graph.nodes:
        text = str(node)
        b_node=(b_nodes and isinstance(node,rdflib.term.BNode))

        if "/" not in text:
            if not b_node:
                continue
        label = f"{text.rsplit("/" ,maxsplit=3)[-2]}/{text.rsplit("/" ,3)[-1]}" if not b_node else text
        if trunc:
            if label.startswith("events"):
                label = truncate_last_path(label)
            if label.startswith("github.com"):
                label = label.split('/')[-1]

        nx_graph.nodes[node]["label"] = label

    # edge labels
    for  _, _, data in nx_graph.edges(data=True):
        pred = data.get("predicate", "").rsplit("/", 1)[-1]
        if short_predicates:
            label = prettify_predicate(pred)
        else:
            label = pred

        data["label"] = label

    for _, data in nx_graph.nodes(data=True):
        if "rdf_type" in data:
            data["rdf_type_str"] = " ".join(data["rdf_type"])

    return nx_graph


def add_formatting_styles(nx_graph: nx.DiGraph, styler:dict) :
    """search the nodes for an identifier containing the key of the ```styler``` then add the
    key's value to the node data,
    :param nx_graph: the graph to add styles to
    :type nx_graph:nx.DiGraph
    :param styler: the styler to use - { part_of_a_node_id : hook_to_style_the_node}
    :type styler:dict
    """
    for key, value in styler.items():
        for node, data in nx_graph.nodes(data=True):
            text = str(node)
            if key in text:
                data['format']=value


def get_the_graph_that_time_forgot()->rdflib.Graph:
    term="""<http://info.cern.ch/hypertext/WWW/TheProject.html> a <http://www.w3.org/ns/prov#Entity>;
            <http://www.w3.org/ns/prov#wasAssociatedWith> <https://www.w3.org/People/Berners-Lee/card.rdf>.
             <https://www.w3.org/People/Berners-Lee/card.rdf> a <http://www.w3.org/ns/prov#Agent>."""
    graph = rdflib.Graph()
    graph.parse(data=term,format="turtle")
    return graph


