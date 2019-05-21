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
		Exception.__init__(self, "Graph has not been populated or has been cleared. Add a graph or run generateRandomGraph() first.")

class noSuchNodeException(Exception):
	def __init__(self, nodeNum):
		Exception.__init__(self, "The node {} does not exist in the graph.".format(nodeNum))

################################################################################################################################

class Embedding:
	def __init__(self, *, graph = None):
		self.theGraph = [] if graph == None else graph

	def generateRandomGraph(self, numNodes, numEdges, *args):
		assert(numNodes > 0), "Number of nodes must be a non-zero integer."
		assert(numEdges >= 0), "Number of edges must be zero or a positive integer."
		assert(len(args) == 0 or len(args) == 1), "Invalid number of arguments."
		if len(args) == 1:
			assert(args[0] > 0), "Allowed redos must be a positive integer."
		# now erase
		if len(self.theGraph) > 0:
			print("Warning: Graph was already populated. Overwriting with randomly generated graph...")
		self.theGraph = []

		allowedRedos = int(args[0]) if len(args) == 1 else 2000
		nodeList = [_ for _ in range(1,numNodes)]
		for _ in range(numEdges):
			t = (nodeList[int(random.uniform(0,len(nodeList)))], nodeList[int(random.uniform(0,len(nodeList)))])
			numOfRedos = 0
			while (t in self.theGraph or t[::-1] in self.theGraph or t[0] == t[1]):
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
			elif len(list(G.neighbors(nodes))) >= 3 and len(list(G.neighbors(nodes))) < 5:
				colorMap.append('green')
			else:
				colorMap.append('blue')

		nx.draw(G, with_labels = True, font_weight = "bold", node_color = colorMap)
		plt.show()

	def getMinDegreeVertices(self, *args):
		assert(len(args) == 0 or len(args) == 1 or len(args) == 2), "Invalid number of arguments."
		if len(self.theGraph) == 0:
			raise emptyGraphException()

		providedNodes = [_ for _ in args[0]] if len(args) >= 1 else []
		providedGraph = [_ for _ in args[1]] if len(args) == 2 else [_ for _ in self.theGraph]
		if len(providedGraph) == 0:
			raise emptyGraphException()

		G = nx.Graph()
		G.add_nodes_from([x for x,y in providedGraph] + [y for x,y in providedGraph])
		G.add_edges_from(providedGraph)

		minDegree = float("inf")
		for nodes in G.nodes():
			if (len(list(G.neighbors(nodes))) < minDegree) and (nodes not in providedNodes):
				minDegree = len(list(G.neighbors(nodes)))
		answer = []
		for nodes in G.nodes():
			if (len(list(G.neighbors(nodes))) == minDegree) and (nodes not in providedNodes):
				answer.append(nodes)

		return answer

	def greedyIndSet(self, *, graph = None):
		answer, discards = [], []
		copy = [_ for _ in self.theGraph] if graph == None else [_ for _ in graph]
		G = nx.Graph()
		G.add_nodes_from([x for x,y in copy] + [y for x,y in copy])
		G.add_edges_from(copy)
		OG = G.number_of_nodes()
		while (G.number_of_nodes() != 0):
			temp = self.getMinDegreeVertices(discards, copy)
			# for now remove the first element
			# remove all it's neighbors
			indexToRemove = int(random.uniform(0, len(temp)))
			N = list(G.neighbors(temp[indexToRemove]))
			# print("Min set is {} and neighbors are {} and removing {}".format(temp, N, temp[indexToRemove]))
			G.remove_node(temp[indexToRemove])
			G.remove_nodes_from(N)
			answer.append(temp[indexToRemove])
			discards.append(temp[indexToRemove])
			discards += N
		return answer

	def greedyBipartite(self):
		L = self.greedyIndSet(graph = self.theGraph)
		stahp = []
		for x,y in self.theGraph:
			if (x not in L) and (y not in L):
				stahp.append((x,y))
		R = self.greedyIndSet(graph = stahp)
		return L,R

	def plotOCTDivision(self, *, left = None, right = None, removeOCT = None):
		if len(self.theGraph) == 0:
			raise emptyGraphException()

		G = nx.Graph()

		G.add_nodes_from([x for x,y in self.theGraph] + [y for x,y in self.theGraph])
		G.add_edges_from(self.theGraph)

		if (removeOCT == True):
			OCTSet = []
			for nodes in G.nodes():
				if nodes not in L and nodes not in R:
					OCTSet.append(nodes)
			G.remove_nodes_from(OCTSet)

		colorMap = []
		for nodes in G.nodes():
			if nodes in left:
				colorMap.append('blue')
			elif nodes in right:
				colorMap.append('red')
			else:
				colorMap.append('gray')

		nx.draw(G, with_labels = True, font_weight = "bold", node_color = colorMap)
		plt.show()

	def clearGraph(self):
		self.theGraph = []

################################################################################################################################

if __name__ == "__main__":
	e = Embedding(graph = [(1,2),(1,5),(1,3),(2,4),(2,5),(3,5),(3,4)])
	#e.generateRandomGraph(10, 25)
	L,R = e.greedyBipartite()
	e.plotOCTDivision(left = L, right = R, removeOCT = False)