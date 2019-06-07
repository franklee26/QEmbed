import networkx as nx

class EMBED_TOOLS:
	def __init__(self, G):
		SHALLOW_COPY = nx.Graph()
		SHALLOW_COPY.add_nodes_from(G.nodes())
		SHALLOW_COPY.add_edges_from(G.edges())
		self.SHALLOW_COPY = SHALLOW_COPY

	def GET_COPY(self):
		return self.SHALLOW_COPY

	def DELETE_NODES(self, nodes):
		# make another copy
		TEMP = nx.Graph()
		TEMP.add_nodes_from(self.SHALLOW_COPY.nodes())
		TEMP.add_edges_from(self.SHALLOW_COPY.edges())
		# usable version
		for n in nodes:
			n1 = list(TEMP.neighbors(n))
			toRestore = []
			for nn in n1:
				if len(list(TEMP.neighbors(nn))) == 1:
					toRestore.append(nn)
			TEMP.remove_node(n)
			for nn in toRestore:
				TEMP.add_node(nn)
		return TEMP

