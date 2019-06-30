import matplotlib.pyplot as plt
import networkx as nx
import dwave_networkx as dnx
import math
import random
import sys
import time
# for general tools: Python passes objects by reference!
import QEmbed.EMBED_TOOLS as ET

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

# helpers

def getChiDimensions(i, j, n):
	# assumes that we do not have a bipartite graph
	# enforce j <= LM and n-i <= LN
	# start with a single 2x2 bipartite
	# enforce I don't get anything more than a 8x8.
	CHECKERED_COUNT = 1
	L, M, N = 1, 1, 2
	while j > L*M and n-i > L*N and CHECKERED_COUNT <= 8:
		# try just incrementing L and M
		L += 1
		M += 1
		CHECKERED_COUNT += 1
	# if this doesn't work, then my last resort is to increase the bipartite
	# enforce I don't get anything larger than a 8x8 bipartite
	# this means my max LM = 64, LN = 64. Should be enough for these problems
	BIPARTITE_COUNT = 1
	while j > L*M and n-i > L*N and BIPARTITE_COUNT <= 8:
		N += 1
		BIPARTITE_COUNT += 1

	if j > L*M or n-i > L*N:
		print("Provided dimensions require a chimera graph larger than 8x8x8. Exiting...")
		return

	return L, M, N

def bipartiteEnsurance(graph, left, right):
	for l in left:
		for r in right:
			if (l,r) not in graph and (r,l) not in graph:
				return False
	return True

################################################################################################################################

class Embedding:
	'''
	Embedding Constructor
	'''
	def __init__(self, *, graph = None):
		self.theGraph = [] if graph == None else graph
		self.theBackup = []

	'''
	generate random graph
	'''
	def generateRandomGraph(self, numNodes = 2, numEdges = 1, allowedRedos = 2000):
		assert(numNodes > 0), "Number of nodes must be a non-zero integer."
		assert(numEdges >= 0), "Number of edges must be zero or a positive integer."
		assert(allowedRedos >= 0 and allowedRedos <= 999999), "Number of redos must be between 0 and 999999"
		if numNodes*(numNodes-1) < numEdges:
			raise overbookedGraphException(allowedRedos)
		# assert(len(args) == 0 or len(args) == 1), "Invalid number of arguments."
		# if len(args) == 1:
		# 	assert(args[0] > 0), "Allowed redos must be a positive integer."
		# now erase
		if len(self.theGraph) > 0:
			print("Warning: Graph was already populated. Overwriting with randomly generated graph...")
			print("Storing previous graph in backup. (Note: this overwrites the backup too.)")
			self.theBackup = self.theGraph
		self.theGraph = []

		#allowedRedos = int(args[0]) if len(args) == 1 else 2000
		nodeList = [_ for _ in range(1,numNodes+1)]
		for _ in range(numEdges):
			t = (nodeList[int(random.uniform(0,len(nodeList)))], nodeList[int(random.uniform(0,len(nodeList)))])
			numOfRedos = 0
			while (t in self.theGraph or t[::-1] in self.theGraph or t[0] == t[1]):
				numOfRedos += 1
				if numOfRedos > allowedRedos:
					raise overbookedGraphException(allowedRedos);
				t = (nodeList[int(random.uniform(0,len(nodeList)))], nodeList[int(random.uniform(0,len(nodeList)))])
			self.theGraph.append(t)

	'''
	standard graph plotting
	'''
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
				colorMap.append('gold')
			elif len(list(G.neighbors(nodes))) >= 7 and len(list(G.neighbors(nodes))) <= 10:
				colorMap.append('orange')
			elif len(list(G.neighbors(nodes))) >= 4 and len(list(G.neighbors(nodes))) < 7:
				colorMap.append('green')
			else:
				colorMap.append('blue')

		nx.draw(G, with_labels = True, font_weight = "bold", node_size = 475, node_color = colorMap, width = 3.25, edge_color = "purple")
		plt.show()

	'''
	returns a list of nodes with the minimum degree
	'''
	def getMinDegreeVertices(self, *, graph = None):
		answer = []
		minDeg = float('inf')
		for nodes in list(graph.nodes()):
			if len(list(graph.neighbors(nodes))) < minDeg:
				minDeg = len(list(graph.neighbors(nodes)))

		for nodes in list(graph.nodes()):
			if len(list(graph.neighbors(nodes))) == minDeg:
				answer.append(nodes)
		return answer

	'''
	input: networkx graph object
	output: a partite for the bipartite graph
	'''
	def greedyIndSet(self, *, graph = None, showProgress = False):
		assert(graph != None), "Error: can not provide empty graph to greedy alg."
		answer = []

		esc = ET.EMBED_TOOLS(graph)
		graphCopy = esc.GET_COPY()

		while (graphCopy.number_of_nodes() != 0):
			temp = self.getMinDegreeVertices(graph = graphCopy)

			# for now remove the first element
			# remove all it's neighbors
			indexToRemove = int(random.uniform(0, len(temp)))
			N = list(graphCopy.neighbors(temp[indexToRemove]))
			if showProgress == True:
				print("Min set is {} and neighbors are {} and removing {}".format(temp, N, temp[indexToRemove]))

			reinsert = []
			# now see if I have to restore some nodes, just iterate over the backup
			for nodes in N:
				if len(list(graphCopy.neighbors(nodes))) == 1:
					reinsert.append(nodes)

			graphCopy.remove_node(temp[indexToRemove])
			# reinsert lone nodes
			for nodes in reinsert:
				graphCopy.add_node(nodes)

			# I also have to remove the neighbors, do the same process
			for nodes in N:
				n1 = list(graphCopy.neighbors(nodes))
				# iterate over and check
				toRestore = []
				for nn in n1:
					if len(list(graphCopy.neighbors(nn))) == 1:
						# deleting this neighbor will screw up this guy
						toRestore.append(nn)
				# saved, now delete
				graphCopy.remove_node(nodes)
				# and recover
				for nn in toRestore:
					graphCopy.add_node(nn)

			answer.append(temp[indexToRemove])

		return answer

	'''
	input: none
	output: get the L, R and perhaps OCT sets from a problem graph
	'''
	def greedyBipartiteSets(self, *, getOCT = None, showProgress = False, ensurance = False):
		assert(getOCT == False or getOCT == True or getOCT == None), "getOCT must be a boolean value."
		G = nx.Graph()
		G.add_nodes_from([x for x,y in self.theGraph] + [y for x,y in self.theGraph])
		G.add_edges_from(self.theGraph)

		et = ET.EMBED_TOOLS(G)

		L = self.greedyIndSet(graph = G, showProgress = showProgress)
		R = self.greedyIndSet(graph = et.DELETE_NODES(L), showProgress = showProgress)

		if ensurance == True:
			MAX_LIMIT, i = 100, 0
			print("Warning: using ensurance slows down biparite calculation and does not necessarily guarantees answer.")
			while bipartiteEnsurance(self.theGraph, L, R) == False and i <= MAX_LIMIT:
				sys.stdout.write("\rTrying ensurance {}/101 time(s)".format(i+1))
				sys.stdout.flush()
				time.sleep(0.01)
				L = self.greedyIndSet(graph = G, showProgress = showProgress)
				R = self.greedyIndSet(graph = et.DELETE_NODES(L), showProgress = showProgress)
				i += 1
			print("QEmbed message: ensurance not required.") if i == 0 else print()
		
		L.sort()
		R.sort()

		if getOCT == True:
			OCT = []
			for nodes in G.nodes():
				if nodes not in L and nodes not in R:
					OCT.append(nodes)
			OCT.sort()
			return L,R,OCT
		return L,R

	'''
	input: none
	output: list of tuples for the bipartite graph
	'''
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

	'''
	input: L and R sets from a Bipartite computed via OCT division
	output: plot of graph but with highlights of the L and R and maybe the OCT set
	'''
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

		nx.draw(G, with_labels = True, font_weight = "bold", node_size = 480, node_color = colorMap, width = 3.25, edge_color = "purple")
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
		dnx.draw_chimera(G, width = 3, edge_color = "purple")

		# abstracting built in exceptions
		try:
			dnx.draw_chimera(H, node_color='r', style='dashed', edge_color='r', width=3, with_labels = True, font_weight = "bold")
		except:
			print("QEmbed Error: provided graph is not bi-partite. Exiting...")
			return

		plt.show()

	'''
	input: bipartite graph with left and right sets (L and R)
	output: plot of chimera graph with bipartite embedded
	'''
	def plotChimeraFromBipartite(self, showMappings = False, L = 2, M = 2, N = 2, *, left = [], right = [], isBipartite = False):
		assert(left != None and right != None), "Must provide non-empty left and right sets."
		assert(L >= 1 and M >= 1 and N >= 1), "Chimera L,M,N topologies must be at least 1."
		if (left == [] or right == []):
			print("Warning: empty left or right sets.")
		answer = []
		labelDict = {}
		if isBipartite == True:
			for i in range(len(left)):
				answer.append((0,0,0,i))
				labelDict[(0,0,0,i)] = "v{}".format(left[i][1])
			for i in range(len(right)):
				answer.append((0,0,1,i))
				labelDict[(0,0,1,i)] = "h{}".format(left[i][1])

		# Mapping bipartite sets. First left set
		else:
			for i, end in left:
				for j in range(1, L+1):
					t = (j, math.ceil((i)/N), 1, ((i)%N)) if ((i)%N) > 0 else (j, math.ceil((i)/N), 1, N)
					answer.append(tuple(k-1 for k in t))
					if (showMappings == True):
						print("Mapping v{} to {}.".format(end, tuple(k-1 for k in t)))
					labelDict[tuple(k-1 for k in t)] = "h{}".format(end)

			for i, end in right:
				for j in range(1, M+1):
					t = (math.ceil((i)/N), j, 2, ((i)%N)) if ((i)%N) > 0 else (math.ceil((i)/N), j, 2, N)
					answer.append(tuple(k-1 for k in t))
					if (showMappings == True):
						print("Mapping h{} to {}.".format(end, tuple(k-1 for k in t)))
					labelDict[tuple(k-1 for k in t)] = "v{}".format(end)

		G = dnx.chimera_graph(L,M,N)
		dnx.draw_chimera(G, width = 4.6, edge_color = "purple", node_size = 480)

		x = dnx.generators.chimera_graph(L,M,N, node_list = answer, coordinates = True)
		dnx.draw_chimera(x, node_color = "red", labels = labelDict, node_size = 480, width = 5, with_labels = True, edge_color = "red", font_weight = "bold", font_size = "medium")
		plt.show()

	'''
	input: L, R and octset
	output: get bipartite graph (list of tuples where first element is where it is mapped to and second is
	the original node name) and maybe the chimaer dimensions
	'''
	def OCTEmbed(self, left = [], right = [], oct = [], getChimeraDimensions = False):
		v, h = [], []
		i = len(oct)
		j = len(left) + i
		n = len(right) + j

		# check if it is already bipartite
		if i == 0:
			# bipartite
			if getChimeraDimensions == True:
				print("Warning: Bipartite graph detected, ensure that bipartite flag is set when plotting.")
				return [(i,i) for i in left], [(i,i) for i in right], 1, 1, max(len(left), len(right))
			return [(i,i) for i in left], [(i,i) for i in right]

		totalIndex = 1
		for nodes in oct:
			v.append((totalIndex, nodes))
			h.append((totalIndex, nodes))
			totalIndex += 1
		for nodes in left:
			v.append((totalIndex, nodes))
			totalIndex += 1
		for nodes in right:
			h.append((totalIndex - i, nodes))
			totalIndex += 1
		if getChimeraDimensions == True:
			# enforce j <= LM and n-i <= LN
			a,b,c = getChiDimensions(i,j,n)
			return v, h, a, b, c
		return v, h

	def plotBipartite(self, left = [], right = []):
		G = dnx.chimera_graph(1,1,max(max([i for i,j in left]), max([i for i,j in right])))
		dnx.draw_chimera(G, width = 4.6, edge_color = "purple", node_size = 480)

		answer = []
		labelDict = {}

		for i in range(len(left)):
			answer.append((0,0,0,i))
			labelDict[(0,0,0,i)] = "{}".format(left[i][1])
		for i in range(len(right)):
			answer.append((0,0,1,i))
			labelDict[(0,0,1,i)] = "{}".format(right[i][1])

		x = dnx.generators.chimera_graph(1,1,max(max([i for i,j in left]), max([i for i,j in right])), node_list = answer, coordinates = True)
		dnx.draw_chimera(x, node_color = "red", labels = labelDict, node_size = 480, width = 5, with_labels = True, edge_color = "red", font_weight = "bold", font_size = "medium")
		plt.show()

	def clearGraph(self):
		self.theGraph = []

	def restoreToBackup(self):
		assert(self.theBackup != []), "Can not restore current graph to an empty backup. Try clearGraph() instead."
		print("Restoring current graph...")
		self.theGraph = self.theBackup

################################################################################################################################

if __name__ == "__main__":
	#e = Embedding(graph = [(1,2),(1,5),(1,3),(2,4),(2,5),(3,5),(3,4)])
	#e.plotGraph()
	#e = Embedding(graph = [(1,4),(1,5),(1,6),(2,4),(2,5),(2,6),(3,4),(3,5),(3,6)])
	#e.plotGraph()
	#L,R,OCT = e.greedyBipartiteSets(getOCT = True)
	# biG = e.greedyBipartiteGraph()
	#print(L,R,OCT)
	#newL, newR, LL, MM, NN = e.OCTEmbed(left = L, right = R, oct = OCT, getChimeraDimensions = True)
	#e.plotBipartite(left = newL, right = newR)
	#e.plotChimeraFromBipartite(left= newL, right = newR, showMappings = False, L = LL, M = MM, N = NN, isBipartite = True)
	#e.plotChimera(2,2,2,biPartite = biG);
	#e.plotOCTDivision(left = L, right = R, removeOCT = True)

	g = [(1,2),(1,3),(1,4),(1,5),(1,6),(1,7),(1,8),(2,3),(2,4),(2,7),(3,4),(3,5),(3,6),(3,7),(3,8),(4,7),(5,8),(5,7),(6,7),(6,8),(4,8)]
	e = Embedding(graph = g)

	e.plotGraph()

	L,R,OCT = e.greedyBipartiteSets(getOCT = True, ensurance = True)
	print(L,R,OCT)

	# i = 0
	# while i <= 100 and bipartiteEnsurance(g,L,R) == False:
	# 	L,R,OCT = e.greedyBipartiteSets(getOCT = True)
	# 	i += 1

	newL, newR, LL, MM, NN = e.OCTEmbed(left = L, right = R, oct = OCT, getChimeraDimensions = True)
	print(newL, newR)
	e.plotBipartite(left = newL, right = newR)
	e.plotChimeraFromBipartite(left= newL, right = newR, showMappings = False, L = 2, M = 2, N = 4, isBipartite = False)
