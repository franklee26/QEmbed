import matplotlib.pyplot as plt
import networkx as nx
import random

# Custom exceptions

################################################################################################################################

class overbookedGraphException(Exception):
	def __init__(self, allowedRedos):
		Exception.__init__(self, "Overbooked graph: can not match edges and nodes with {} redos. Try with less edges or more nodes or increasing the number of redos.".format(allowedRedos))

class emptyGraphException(Exception):
	def __init__(self):
		Exception.__init__(self, "Graph has not yet been populated or has been cleared. Run generateRandomGraph() first.")

class noSuchNodeException(Exception):
	def __init__(self, nodeNum):
		Exception.__init__(self, "The node {} does not exist in the graph.".format(nodeNum))

################################################################################################################################

class Embedding:
	def __init__(self):
		self.theGraph = []

	def generateRandomGraph(self, numNodes, numEdges, *args):
		assert(numNodes > 0), "Number of nodes must be a non-zero integer."
		assert(numEdges >= 0), "Number of edges must be zero or a positive integer."
		assert(len(args) == 0 or len(args) == 1), "Invalid number of arguments."
		if len(args) == 1:
			assert(args[0] > 0), "Allowed redos must be a positive integer."

		allowedRedos = int(args[0]) if len(args) == 1 else 2000
		nodeList = [_ for _ in range(1,numNodes)]
		for _ in range(numEdges):
			t = (nodeList[int(random.uniform(0,len(nodeList)))], nodeList[int(random.uniform(0,len(nodeList)))])
			numOfRedos = 0
			while (t in self.theGraph or t[::-1] in self.theGraph):
				numOfRedos += 1
				if numOfRedos > allowedRedos:
					raise overbookedGraphException(allowedRedos);
				t = (nodeList[int(random.uniform(0,len(nodeList)))], nodeList[int(random.uniform(0,len(nodeList)))])
			self.theGraph.append(t)

	def plotGraph(self):
		if len(self.theGraph) == 0:
			raise emptyGraphException()

		G = nx.Graph()

		G.add_nodes_from([x for x,y in self.theGraph] + [y for x,y in self.theGraph])
		G.add_edges_from(self.theGraph)

		colorMap = []
		for nodes in G.nodes():
			if len(list(G.neighbors(nodes))) > 12:
				colorMap.append('red')
			elif len(list(G.neighbors(nodes))) > 10 and len(list(G.neighbors(nodes))) <= 12:
				colorMap.append('orange')
			elif len(list(G.neighbors(nodes))) >= 5 and len(list(G.neighbors(nodes))) <= 10:
				colorMap.append('yellow')
			elif len(list(G.neighbors(nodes))) >= 2 and len(list(G.neighbors(nodes))) < 5:
				colorMap.append('green')
			else:
				colorMap.append('blue')

		nx.draw(G, with_labels = True, font_weight = "bold", node_color = colorMap)
		plt.show()

	def getMinDegreeVertices(self, *args):
		assert(len(args) == 0 or len(args) == 1), "Invalid number of arguments."

		if len(self.theGraph) == 0:
			raise emptyGraphException()

		providedNodes = [_ for _ in args[0]] if len(args) == 1 else []

		# check if the nodes actually exist in the graph
		for prov in providedNodes:
			if prov not in [x for x,y in self.theGraph] + [y for x,y in self.theGraph]:
				raise noSuchNodeException(prov)

		G = nx.Graph()
		G.add_nodes_from([x for x,y in self.theGraph] + [y for x,y in self.theGraph])
		G.add_edges_from(self.theGraph)

		minDegree = float("inf")
		for nodes in G.nodes():
			if (len(list(G.neighbors(nodes))) < minDegree) and (nodes not in providedNodes):
				minDegree = len(list(G.neighbors(nodes)))

		answer = []
		for nodes in G.nodes():
			if (len(list(G.neighbors(nodes))) == minDegree) and (nodes not in providedNodes):
				answer.append(nodes)

		return answer

	def clearGraph(self):
		self.theGraph = []

################################################################################################################################

if __name__ == "__main__":
	e = Embedding()
	e.generateRandomGraph(100, 300)
	print(e.getMinDegreeVertices())
	e.plotGraph()