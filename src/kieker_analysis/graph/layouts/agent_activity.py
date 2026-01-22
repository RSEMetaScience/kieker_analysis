import math

import networkx as nx
import rdflib

from kieker_analysis.graph.layouts.util import get_nx_adjacency

def layout_agent_events(nxg: nx.DiGraph,
                        agent_id: str,
                        r_event_types: float = 200.0,
                        ):
    """
    """
    nodes = list(nxg.nodes)
    # group nodes by attributes ---
    main_agent_id = None
    agents = [n_id for n_id, data in nxg.nodes(data=True)
              if data.get("rdf_type_str") == "http://www.w3.org/ns/prov#Agent"]
    secondary_agents = []
    if not agents:
        raise ValueError("No agent node found with rdf_type_str=prov#Agent")

    # make the main agent the central node and collect any others as secondary agents
    for agent in agents:
        if agent == rdflib.term.URIRef(f'https://github.com/{agent_id}'):
            main_agent_id = agent
        elif agent == rdflib.term.URIRef("https://www.w3.org/People/Berners-Lee/card.rdf"):
            main_agent_id = agent
        else:
            secondary_agents.append(agent)

    if not main_agent_id:
        raise ValueError("the main agent was not found in the graph")

    creation_event_id = rdflib.term.URIRef('http://purl.org/github2prov/created')
    if creation_event_id not in nxg:
        creation_event_id = None

    main_agent_x, main_agent_y = 0.0, 0.0
    nxg.nodes[main_agent_id]["pos"] = (main_agent_x, main_agent_y)

    # adjacency map
    adjacency = get_nx_adjacency(nxg)
    #  the event types except creation which we treat a bit differently
    event_type_ids = [n_id for n_id, data in nxg.nodes(data=True) if data.get("format") == "outer"]
    # the inner nodes:this adjacent to the m ain agent go between it and the event types
    inner_node_ids = {n_id for n_id, data in nxg.nodes(data=True) if data.get("format") == "inner"}

    # collect inner event nodes that are not adjacent to the main agent - these are events by secondary agents
    creation_nodes = {n_id for n_id in inner_node_ids if n_id not in adjacency[main_agent_id]}

    # place ALL event types on a circle around the main agent,
    # but push the creation event type further out along its angle
    event_type_count = len(event_type_ids)
    angle_offset = math.radians(30)
    for i, event_type_id in enumerate(event_type_ids):
        angle = 2 * math.pi * i / event_type_count + angle_offset if event_type_count > 0 else 0.0

        # longer radius for the creation event type
        if creation_event_id is not None and event_type_id == creation_event_id:
            radius = 1.4 * r_event_types  # tweak me
        else:
            radius = r_event_types

        event_x = main_agent_x + radius * math.cos(angle)
        event_y = main_agent_y + radius * math.sin(angle)
        nxg.nodes[event_type_id]["pos"] = (event_x, event_y)

    # put inner (grey) nodes between agent and each event type ---
    assigned_events = set()  # aviod moving same node multiple times

    for event_type_id in event_type_ids:
        event_type_x, event_type_y = nxg.nodes[event_type_id]["pos"]

        # neighbours of this event type
        neighbours = adjacency[event_type_id]
        # pick the neighbour that is an inner node (there should be exactly one after collapse)
        inner_candidates = [nid for nid in neighbours if (nid in inner_node_ids and nid not in creation_nodes)]
        if not inner_candidates:
            continue
        inner_node_id = inner_candidates[0]
        if inner_node_id in assigned_events:
            continue

        # halfway between agent -> event type
        inner_x = (main_agent_x + event_type_x) / 2.0
        inner_y = (main_agent_y + event_type_y) / 2.0

        nxg.nodes[inner_node_id]["pos"] = (inner_x, inner_y)
        assigned_events.add(inner_node_id)

    # secondary agents need to be arranged around the creation node with their collapsed events nodes between them
    # and the creation node
    if creation_event_id is not None and secondary_agents:
        created_x, created_y = nxg.nodes[creation_event_id]["pos"]
        # the size of the little circle
        r_agents = 0.6 * r_event_types  # radius of semicircle around creation node
        num_second_agents = len(secondary_agents)
        if num_second_agents == 1:
            angles = [0.0]
        else:
            start = -math.pi / 3
            end = math.pi / 3
            angles = [
                start + (end - start) * i / (num_second_agents - 1)
                for i in range(num_second_agents)
            ]

        for angle, agent in zip(angles, secondary_agents):
            ax = created_x + r_agents * math.cos(angle + angle_offset)
            ay = created_y + r_agents * math.sin(angle + angle_offset)
            nxg.nodes[agent]["pos"] = (ax, ay)

            # this agent's creation inner nodes = neighbours ∩ creation_nodes
            agent_neighbours = adjacency[agent]
            agent_creation_inners = [
                nid for nid in agent_neighbours
                if nid in creation_nodes
            ]
            for inner_id in agent_creation_inners:
                ix = (ax + created_x) / 2.0
                iy = (ay + created_y) / 2.0
                nxg.nodes[inner_id]["pos"] = (ix, iy)

    # for agent in secondary_agents:
    #     if "pos" not in nxg.nodes[agent]:
    #         adjacent_nodes=adjacency[agent]
    #         for node in adjacent_nodes:
    #             if "pos" in nxg.nodes[node]:
    #                 x, y = nxg.nodes[node]["pos"]
    #                 # need to fix this to assign the position
    #                 next_pos = (x+130, y+130)
    #                 nxg.nodes[agent]["pos"] = next_pos

    # ensure every node has a position (fallback for oddments) ---
    for node_id in nodes:
        if "pos" not in nxg.nodes[node_id]:
            nxg.nodes[node_id]["pos"] = (main_agent_x + 14, main_agent_y + 16)
