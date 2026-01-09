import igraph as ig
from app.core.graph import get_community_subgraph

def test_subgraph():
    # Create a simple graph
    # 0-1-2 (Comm 0), 3-4 (Comm 1)
    g = ig.Graph()
    g.add_vertices(5)
    g.vs['name'] = ['A', 'B', 'C', 'D', 'E']
    g.add_edges([(0,1), (1,2), (3,4)])
    
    communities = {
        'A': {'level_1': 0},
        'B': {'level_1': 0},
        'C': {'level_1': 0},
        'D': {'level_1': 1},
        'E': {'level_1': 1}
    }
    
    print("Testing get_community_subgraph...")
    try:
        # Test getting Community 0 (should be A, B, C)
        print("Requesting subgraph for Community 0...")
        subgraph_0 = get_community_subgraph(g, communities, community_id=0, level='level_1')
        print(f"Subgraph 0 vertex count: {subgraph_0.vcount()}")
        print(f"Subgraph 0 vertex names: {sorted(subgraph_0.vs['name'])}")
        
        # Test getting Community 1 (should be D, E)
        print("Requesting subgraph for Community 1...")
        subgraph_1 = get_community_subgraph(g, communities, community_id=1, level='level_1')
        print(f"Subgraph 1 vertex count: {subgraph_1.vcount()}")
        print(f"Subgraph 1 vertex names: {sorted(subgraph_1.vs['name'])}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_subgraph()
