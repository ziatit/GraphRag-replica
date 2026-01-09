class Summarizer:
    def __init__(self, graph: ig.Graph, communities: dict):
        self.graph = graph
        self.communities = communities