import matplotlib.pyplot as plt
import networkx as nx
import dwave_networkx as dnx
import math
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

	def greedyBipartiteSets(self, *, getOCT = None):
		assert(getOCT == False or getOCT == True or getOCT == None), "getOCT must be a boolean value."
		L = self.greedyIndSet(graph = self.theGraph)
		stahp = []
		for x,y in self.theGraph:
			if (x not in L) and (y not in L):
				stahp.append((x,y))
		R = self.greedyIndSet(graph = stahp)
		if getOCT == True:
			OCT = []
			G = nx.Graph()
			G.add_nodes_from([x for x,y in self.theGraph] + [y for x,y in self.theGraph])
			G.add_edges_from(self.theGraph)
			for nodes in G.nodes():
				if nodes not in L and nodes not in R:
					OCT.append(nodes)
			return L,R,OCT
		return L,R

	def greedyBipartiteGraph(self):
		L = self.greedyIndSet(graph = self.theGraph)
		stahp = []
		for x,y in self.theGraph:
			if (x not in L) and (y not in L):
				stahp.append((x,y))
		R = self.greedyIndSet(graph = stahp)
		answer = []
		# build a graph for nodes
		for x,y in self.theGraph:
			if ((x not in L) and (x not in R)) or ((y not in L) and (y not in R)):
				# OCT
				pass
			else:
				answer.append((x,y))
		return answer

	def plotOCTDivision(self, *, left = None, right = None, removeOCT = None):
		assert(left != None and right != None), "Must provide left and right sets."
		assert(removeOCT == False or removeOCT == True or removeOCT == None), "removeOCT must be a boolean value."

		if len(self.theGraph) == 0:
			raise emptyGraphException()

		G = nx.Graph()

		G.add_nodes_from([x for x,y in self.theGraph] + [y for x,y in self.theGraph])
		G.add_edges_from(self.theGraph)

		if (removeOCT == True):
			OCTSet = []
			for nodes in G.nodes():
				if nodes not in left and nodes not in right:
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

	def plotChimera(self, l, m, n, *, biPartite = None):
		assert(biPartite != None and len(biPartite) >= 2), "A bipartite graph w/ >= 2 nodes must be provided."
		if len(self.theGraph) == 0:
			raise emptyGraphException()

		H = nx.Graph()

		H.add_nodes_from([x for x,y in biPartite] + [y for x,y in biPartite])
		H.add_edges_from(biPartite)

		# need to find correct dimensions
		# first need L and R sizes
		# assuming this bipartite set is the one provided in the args
		LSet, RSet, OCTSet = self.greedyBipartiteSets(getOCT = True)
		left, right, OCT = len(LSet), len(RSet), len(OCTSet)
		
		G = dnx.chimera_graph(l,m,n)
		dnx.draw_chimera(G)

		# abstracting built in exceptions
		try:
			dnx.draw_chimera(H, node_color='r', style='dashed', edge_color='r', width=3, with_labels = True, font_weight = "bold")
		except:
			print("QEmbed Error: provided graph is not bi-partite. Exiting...")
			return

		plt.show()

	# given a bipartite graph, plot the chimera graph
	def plotChimeraFromBipartite(self, showMappings = False, L = 2, M = 2, N = 2, *, left = [], right = []):
		assert(left != None and right != None), "Must provide non-empty left and right sets."
		assert(L >= 1 and M >= 1 and N >= 1), "Chimera L,M,N topologies must be at least 1."
		answer = []
		labelDict = {}
		# Mapping bipartite sets. First left set:
		for i in range(0, len(left)):
			for j in range(0,M):
				t = (j, math.ceil(i/L), 0, (i%L)-1) if (i%L)-1 >= 0 else (j, math.ceil(i/L), 0, 0)
				answer.append(t)
				if (showMappings == True):
					print("Mapping v{} to {}.".format(i+1, t))
				labelDict[t] = "v{}".format(i+1)
		# then right set
		for i in range(0, len(right)):
			for j in range(0,N):
				t = (math.ceil(i/L), j, 1, (i%L)-1) if (i%L)-1 >= 0 else (math.ceil(i/L), j, 1, 0)
				answer.append(t)
				if (showMappings == True):
					print("Mapping h{} to {}.".format(i+1, t))
				labelDict[t] = "h{}".format(i+1)

		# L,M,N = 2,2,2
		# for keys in labelDict:
		# 	if keys[0] + 1 > L: L = keys[0] + 1
		# 	if keys[1] + 1 > M: M = keys[1] + 1
		# 	if keys[3] + 1 > N: N = keys[3] + 1

		G = dnx.chimera_graph(L,M,N)
		dnx.draw_chimera(G)

		x = dnx.generators.chimera_graph(N,L,M, node_list = answer, coordinates = True)
		dnx.draw_chimera(x, node_color = "red", labels = labelDict, with_labels = True, edge_color = "red", font_weight = "bold", font_size = "medium")
		plt.show()

	def clearGraph(self):
		self.theGraph = []

################################################################################################################################

if __name__ == "__main__":
	e = Embedding(graph = [(1,2),(1,5),(1,3),(1,4),(2,4),(2,5),(3,5),(3,4)])

	#e = Embedding()
	#e.generateRandomGraph(20, 70)
	L,R,OCT = e.greedyBipartiteSets(getOCT = True)
	biG = e.greedyBipartiteGraph()
	e.plotChimeraFromBipartite(left= L, right = R)
	#e.plotChimera(2,2,2,biPartite = biG);
	#e.plotOCTDivision(left = L, right = R, removeOCT = True)