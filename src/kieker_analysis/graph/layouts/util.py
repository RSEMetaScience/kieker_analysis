from collections import defaultdict
from uuid import uuid4

import networkx as nx
from ipycytoscape import CytoscapeWidget


def build_id_to_node(cyto, id_attr="id") -> dict:
    """ Build a mapping: node_id -> cytoscape node object.
    :param cyto: the CytoscapeWidget that is displaying the graph
    :type cyto: CytoscapeWidget
    :param id_attr: Node data attribute that holds the identifier used as a key
    :type id_attr: str
    :returns: a mapping of node_id -> cytoscape node object
    :rtype: dict

    """
    mapping = {}
    for node in cyto.graph.nodes:
        data = node.data or {}
        node_id = data.get(id_attr)
        if node_id is None:
            node_id = str(node)
        mapping[node_id] = node
    return mapping


def build_adjacency(cyto, id_to_node):
    """Build undirected adjacency: node_id -> set(node_id). uses the existing edge list, assuming each edge has
    data["source"] and data["target"] set to node IDs.
    :param cyto: the CytoscapeWidget that is displaying the graph
    :type cyto: CytoscapeWidget
    :param id_to_node: a mapping of node_id -> cytoscape node object
    :type id_to_node: dict
    :returns: an adjancency maop
    :rtype: dict
    """
    adjacency = {nid: set() for nid in id_to_node.keys()}
    for edge in cyto.graph.edges:
        s = edge.data.get("source")
        t = edge.data.get("target")
        if s in adjacency and t in adjacency:
            adjacency[s].add(t)
            adjacency[t].add(s)
    return adjacency


def get_nx_adjacency(nxg: nx.DiGraph):
    """build an undirected adjacency map for each node in an nx.DiGraph: node_id -> set of adjacent nodes in
    either direction
    """
    adjacency = {}
    for node_id in nxg.nodes:
        predecessors = set(nxg.predecessors(node_id))
        successors = set(nxg.successors(node_id))
        adjacency[node_id] = predecessors | successors
    return adjacency


def collapse_nodes(
        nxg: nx.DiGraph,
        group_attr: str = "format",
        group_id: str = "inner",
        id_prefix: str = "agg",
):
    """
    Collapse nodes of a given group so that nodes with the same neigbours are merged into one aggregated node with
    count metadata recording how many nodes were collapsed.
    :param nxg: the network x graph we are displaying
    :type nxg: nx.DiGraph
    :param group_attr: the node attribute used for grouping
    :type group_attr: str
    :param group_id: the group_attr value to be used for grouping
    :type group_id: str
    :param id_prefix: the prefix used for new node IDs
    :type id_prefix: str

    """
    # make an undirected adjancency map: node_id -> set(neighbour nodes)
    adjacency: dict = get_nx_adjacency(nxg)
    # for node_id, n in nxg.nodes(data=True):
    #     predecessors = set(nxg.predecessors(node_id))
    #     successors = set(nxg.successors(node_id))
    #     adjacency[node_id] = predecessors | successors

    collapsible = {
        node_id: tuple(sorted(adjacency[node_id]))  # the connected nodes, sorted so we can also use them as keys
        for node_id, data in nxg.nodes(data=True)  # ...of every node
        if data.get(group_attr) == group_id  # in our fromatting group
        if len(adjacency[node_id]) == 2  # with a node degree of 2 (does this matter more generally?)
    }

    groups = defaultdict(list)
    for node_id, key in collapsible.items():
        groups[key].append(node_id)

    to_remove: list[str] = []
    for (n1, n2), node_ids in groups.items():
        if len(node_ids) <= 1:  # no point collapsing a single node, but we need a size
            node_data = dict(nxg.nodes(node_ids[0]))
            node_data.update(
                {
                    group_attr: group_id,
                    "node_count": 1,
                    "size": 1,
                    "label": "1"
                })
            continue

        neighbours = (n1, n2)
        count = len(node_ids)

        # base the new node on the first colapsable node
        base_node_id = node_ids[0]
        new_data = dict(nxg.nodes[base_node_id])
        new_id = f"{id_prefix}_{uuid4()}"
        new_data.update(
            {
                "id": new_id,
                group_attr: group_id,
                "node_count": count,
                "size": get_aggregate_node_size(count),
                "label": str(count)
            }
        )

        nxg.add_node(new_id, **new_data)
        for neighbour_id in neighbours:
            nxg.add_edge(new_id, neighbour_id)
        to_remove.extend(node_ids)

    for node_id in to_remove:
        if node_id in nxg:
            nxg.remove_node(node_id)


def truncate_last_path(uri: str, n: int = 7) -> str:
    """Truncate an identifier by shortening the last part. The truncation replaces all but the last ```n``` characters
     with an ellipse (...) e.g,
     :param uri:the url to truncate
     :type uri:str
     :param n: the number of characters to truncate defaults to 5
     :type n:int
     :return: the truncated uri
     :rtype: str
     """
    split = uri.split("/")
    identifier = f"...{split[1]}"
    return f"{split[0]}/{identifier[-n:]}"


def prettify_predicate(predicate: str) -> str:
    if predicate.startswith("prov#"):
        return predicate.rsplit("#", 1)[-1]
    if predicate.startswith("22-rdf-syntax-ns#type"):
        return "rdf:type"
    return predicate


def get_aggregate_node_size(x: int,
                            in_min: int = 1,
                            in_max: int = 100,
                            out_min: int = 5,
                            out_max: int = 80,
                            k: float = 3.0,  # bigger = more front-loaded increase
                            ) -> int:
    if not (in_min <= x <= in_max):
        raise ValueError(f"x must be in [{in_min}, {in_max}], got {x}")

    # Normalize to [0, 1]
    t = (x - in_min) / (in_max - in_min)
    # Concave "ease-out" curve: steep early, flatter late
    eased = 1.0 - (1.0 - t) ** k
    y = out_min + (out_max - out_min) * eased
    return int(round(y))


def make_cyto_from_nx(nxg: nx.DiGraph, style) -> CytoscapeWidget:
    """
    create a CytoscapeWidget from a NetworkX graph that already has
    'pos' attributes on nodes (x, y).
    """
    cyto = CytoscapeWidget()
    cyto.graph.add_graph_from_networkx(nxg)

    # copy 'pos' into widget node.position so we can use the 'preset' layout
    id_to_node = {}
    for node in cyto.graph.nodes:
        data = node.data or {}
        node_id = data.get("id") or str(node)
        id_to_node[str(node_id)] = node

    for node_id, (x, y) in nx.get_node_attributes(nxg, "pos").items():
        widget_node = id_to_node.get(str(node_id))
        if widget_node is not None:
            widget_node.position = {"x": x, "y": y}

    cyto.set_style(style)
    cyto.set_layout(name="preset", animate=False)
    return cyto
