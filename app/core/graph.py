import json
import leidenalg
import igraph as ig

def clean_json(json_path: str):
    with open(json_path, 'r') as f:
        chunks = json.load(f)

    unique_entities = {}
    unique_relationships = {}
    
    for chunk in chunks:
        if chunk.get("status") != "success":
            continue
            
        data = chunk.get("data")
        if not data:
            continue

        for entity in data.get("entities", []):
            name = entity.get("name", "").lower()
            if not name:
                continue
                
            if name not in unique_entities:
                unique_entities[name] = {
                        "name": entity.get("name"), # Keep original casing for display if needed, or use lower
                        "type": entity.get("type"),
                        "description": set([entity.get("description", "")])
                }   
            else:
                unique_entities[name]["description"].add(entity.get("description", ""))

        for relationship in data.get("relationships", []):
            source = relationship.get("source", "")
            target = relationship.get("target", "")
            if not source or not target:
                continue
                
            rel_type = relationship.get("relationship_type", "related") # Handle missing type
            
            # Using a consistent ID format
            rel_id = f"{source}_{rel_type}_{target}"

            if rel_id not in unique_relationships:
                unique_relationships[rel_id] = {
                    "source": source,
                    "target": target,
                    "type": rel_type,
                    "description": set([relationship.get("description", "")]),
                    "strength": float(relationship.get("strength", 1.0))
                }
            else:
                unique_relationships[rel_id]["description"].add(relationship.get("description", ""))
                unique_relationships[rel_id]["strength"] = max(unique_relationships[rel_id]["strength"], float(relationship.get("strength", 1.0)))

    # Convert sets to lists for JSON serialization/output
    for entity in unique_entities.values():
        entity["description"] = list(entity["description"])
        
    for rel in unique_relationships.values():
        rel["description"] = list(rel["description"])

    return {
        "entities": list(unique_entities.values()),
        "relationships": list(unique_relationships.values())
    }

def build_graph(json_path: str) -> ig.Graph:
    """
    Builds an igraph.Graph directly from the JSON data.
    """
    data = clean_json(json_path)
    
    g = ig.Graph(directed=False) 
    
    entities = data['entities']
    num_vertices = len(entities)
    g.add_vertices(num_vertices)
    
    name_to_index = {entity['name']: i for i, entity in enumerate(entities)}
    
    g.vs['name'] = [e['name'] for e in entities]
    g.vs['type'] = [e['type'] for e in entities]
    g.vs['description'] = [e['description'] for e in entities]
    
    edges = []
    weights = []
    edge_types = []
    edge_descriptions = []
    
    for rel in data['relationships']:
        source = rel['source']
        target = rel['target']
        
        if source in name_to_index and target in name_to_index:
            edges.append((name_to_index[source], name_to_index[target]))
            weights.append(rel['strength'])
            edge_types.append(rel['type'])
            edge_descriptions.append(rel['description'])
            
    g.add_edges(edges)
    g.es['weight'] = weights
    g.es['type'] = edge_types
    g.es['description'] = edge_descriptions
    
    # --- Optimization: Remove small disconnected components ---
    # Many entities might be isolated or form tiny islands (e.g. size 1 or 2).
    # These create noise and unnecessary communities.
    
    # Get connected components (weakly connected for directed, but we built undirected/mixed)
    components = g.components(mode="weak")
    
    # Keep only components with size >= 3 (configurable)
    # This removes isolated nodes and pairs, keeping only more significant structures.
    to_delete = []
    for subgraph_indices in components:
        if len(subgraph_indices) < 3:
            to_delete.extend(subgraph_indices)
            
    if to_delete:
        g.delete_vertices(to_delete)
        
    return g

def find_communities(graph: ig.Graph):
    """
    Detect communities using Leiden algorithm hierarchically (2 levels).
    Returns a dictionary: {node_name: {'level_1': int, 'level_0': int}}
    Level 1: Detailed communities (base level)
    Level 0: Super-communities (clusters of Level 1 communities)
    """
    # --- Level 1: Base Communities ---
    partition_1 = leidenalg.find_partition(
        graph, 
        leidenalg.ModularityVertexPartition, 
        weights=graph.es['weight']
    )
    
    # Membership list for Level 1 (node_idx -> comm_id)
    membership_1 = partition_1.membership
    
    # --- Level 0: Super Communities ---
    # Create a graph where nodes are Level 1 communities
    # contract_vertices merges nodes based on membership
    # simplify combines multiple edges into one (summing weights)
    
    # We need a copy because contract_vertices modifies the graph in-place (or returns a modified one, but let's be safe)
    # Actually contract_vertices keeps edge attributes but we need to sum them.
    
    # Efficient way in igraph:
    # 1. Contract vertices
    g_level_0 = graph.copy()
    g_level_0.contract_vertices(membership_1)
    
    # 2. Simplify to merge edges and sum weights
    # combine_edges={'weight': sum} tells it to sum the 'weight' attribute
    # We drop other attributes like 'type' or 'description' as they don't make sense for aggregated edges
    g_level_0.simplify(combine_edges={'weight': sum})
    
    # Run Leiden on this coarser graph
    partition_0 = leidenalg.find_partition(
        g_level_0,
        leidenalg.ModularityVertexPartition,
        weights=g_level_0.es['weight']
    )
    
    membership_0 = partition_0.membership
    
    # --- Map back to nodes ---
    communities = {}
    for i, node_vertex in enumerate(graph.vs):
        node_name = node_vertex['name']
        level_1_id = membership_1[i]
        level_0_id = membership_0[level_1_id] # The super-community of the level 1 community
        
        communities[node_name] = {
            'level_1': level_1_id,
            'level_0': level_0_id
        }
        
    return communities

def get_community_subgraph(graph: ig.Graph, communities: dict, community_id: int, level: str = 'level_1'):
    """
    Returns a subgraph containing only the vertices of a specific community.
    """
    # Find all node names that belong to this community_id at this level
    nodes_in_community = [
        name for name, comms in communities.items() 
        if comms.get(level) == community_id
    ]
    
    # igraph can select vertices by name if the 'name' attribute is set
    return graph.subgraph(nodes_in_community)

def visualize_graph(graph: ig.Graph, communities: dict, output_path: str, level: str = 'level_1'):
    """
    Visualizes the graph using matplotlib and saves it to a file.
    level: 'level_1' (detailed) or 'level_0' (super-communities)
    """
    import matplotlib.pyplot as plt
    
    # Extract the requested level for coloring
    comm_ids = [c.get(level) for c in communities.values()]
    unique_comms = set(comm_ids)
    num_communities = len(unique_comms)
    
    palette = ig.RainbowPalette(n=num_communities)
    
    # Map comm_id to color
    # We need a consistent mapping because comm_ids might not be 0..N-1 perfectly if filtered, 
    # but usually they are.
    
    vertex_colors = []
    for vertex in graph.vs:
        comm_data = communities.get(vertex['name'])
        if comm_data and level in comm_data:
            comm_id = comm_data[level]
            color = palette.get(comm_id)
            vertex_colors.append(color)
        else:
            vertex_colors.append((0.5, 0.5, 0.5, 1.0))
            
    # Plot using matplotlib backend
    fig, ax = plt.subplots(figsize=(12, 12))
    ig.plot(
        graph, 
        target=ax,
        layout=graph.layout("kk"),
        vertex_color=vertex_colors,
        vertex_label=None, 
        vertex_size=15,
        edge_width=0.5,
        edge_color='#AAAAAA'
    )
    
    plt.title(f"Entity Graph - Communities ({level})")
    plt.savefig(output_path)
    plt.close()