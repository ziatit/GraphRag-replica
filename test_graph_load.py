import sys
import os
import json

# Add the current directory to sys.path to allow importing from app
sys.path.append(os.getcwd())

from app.core.graph import build_graph, find_communities, visualize_graph
import igraph as ig

def test_load():
    json_path = "output/extracted_entities_whole_book.json"
    
    if not os.path.exists(json_path):
        print(f"File not found: {json_path}")
        return

    try:
        print("Building graph...")
        graph = build_graph(json_path)
        
        print("Successfully built igraph.")
        print(f"Vertices count: {graph.vcount()}")
        print(f"Edges count: {graph.ecount()}")
        
        if graph.vcount() > 0:
            print(f"Sample Vertex Name: {graph.vs[0]['name']}")
            
        print("\nFinding communities (Hierarchical)...")
        communities = find_communities(graph)
        
        # Count unique communities at each level
        level_1_ids = set(c['level_1'] for c in communities.values())
        level_0_ids = set(c['level_0'] for c in communities.values())
        
        print(f"Found {len(level_1_ids)} Level 1 communities (Detailed).")
        print(f"Found {len(level_0_ids)} Level 0 communities (Super-communities).")
        
        # Print first few community assignments
        print("\nSample Community Assignments:")
        for name, comms in list(communities.items())[:5]:
            print(f"{name}: L1={comms['level_1']}, L0={comms['level_0']}")
            
        print("\nGenerating visualizations...")
        
        visualize_graph(graph, communities, "graph_visualization_L1.png", level='level_1')
        print("Saved graph_visualization_L1.png")
        
        visualize_graph(graph, communities, "graph_visualization_L0.png", level='level_0')
        print("Saved graph_visualization_L0.png")
            
    except Exception as e:
        print(f"Error testing graph: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_load()
