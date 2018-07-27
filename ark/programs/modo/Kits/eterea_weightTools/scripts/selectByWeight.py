#python

"""  
	Select By Weight script 1.0  by Richard Rodriguez (gm770)
	- Tested on Modo 501 and 401sp5 for PC
	
	How to use:
	- Run with no Edges selected, it will select all weighted edges
	- Run with Edges selected, it will select all edges that have 
	the same weight as any of the selected edges
"""

import lx


main=lx.eval("query layerservice layers ? main")
edge_cnt = lx.eval("query layerservice edge.N ? all")
if edge_cnt != 0:
	edge_list = []
	weight_list = []

	for x in range(edge_cnt):
		w = lx.eval("query layerservice edge.creaseWeight ? %s" % x)
		s = lx.eval("query layerservice edge.selected ? %s" % x)
		if s == 1  and  w not in weight_list:
			weight_list.append(w)
		a,b = lx.eval("query layerservice edge.vertList ? %s" % x)
		edge = {"i":x, "w":w, "a":a, "b":b}
		edge_list.append(edge)

	wl_cnt = len(weight_list)
	lx.eval("select.drop edge")
	if wl_cnt != 0:
		for edge in edge_list: 
			if edge['w'] in weight_list:
				lx.eval("select.element %s edge add %s %s" % (main, edge['a'], edge['b']) )
	else:
		for edge in edge_list:
			if edge['w'] != 0:
				lx.eval("select.element %s edge add %s %s" % (main, edge['a'], edge['b']) )	