# ## L’Indifferenza dell’Amore Cosmico I
# ### _(The Indifference of the Cosmic Love I)_
# 
# for flauto d’amore (or flute(s))<br>
# cosmic rays and electronics<br>
# (arbitrary duration)
# 
# 
# to Ginevra Petrucci for the Flauto d’Amore Project
# 
# ©2021, Marco Buongiorno Nardelli


import warnings
warnings.filterwarnings("ignore") 

import random,itertools,glob,os,json
import numpy as np
import networkx as nx
import pandas as pd
from graphviz import Digraph,Graph
import svgutils.transform as st

sec = 'Section 1'
nxmodel = 'BA'

def chinese_postman(graph,starting_node=None,verbose=False):
        
    def get_shortest_distance(graph, pairs, edge_weight_name):
        return {pair : nx.dijkstra_path_length(graph, pair[0], pair[1], edge_weight_name) for pair in pairs}

    def create_graph(node_pairs_with_weights, flip_weight = True):
        graph = nx.Graph()
        for k,v in node_pairs_with_weights.items():
            wt = -v if flip_weight else v
            graph.add_edge(k[0], k[1], **{'distance': v, 'weight': wt})
        return graph

    def create_new_graph(graph, edges, starting_node=None):
        g = nx.MultiGraph()
        for edge in edges:
            aug_path  = nx.shortest_path(graph, edge[0], edge[1], weight="distance")
            aug_path_pairs  = list(zip(aug_path[:-1],aug_path[1:]))

            for aug_edge in aug_path_pairs:
                aug_edge_attr = graph[aug_edge[0]][aug_edge[1]]
                g.add_edge(aug_edge[0], aug_edge[1], attr_dict=aug_edge_attr)
        for edge in graph.edges(data=True):
            g.add_edge(edge[0],edge[1],attr_dict=edge[2:])
        return g

    def create_eulerian_circuit(graph, starting_node=starting_node):
        return list(nx.eulerian_circuit(graph,source=starting_node))
    
    odd_degree_nodes = [node for node, degree in dict(nx.degree(graph)).items() if degree%2 == 1]
    odd_degree_pairs = itertools.combinations(odd_degree_nodes, 2)
    odd_nodes_pairs_shortest_path = get_shortest_distance(graph, odd_degree_pairs, "distance")
    graph_complete_odd = create_graph(odd_nodes_pairs_shortest_path, flip_weight=True)
    if verbose:
        print('Number of nodes (odd): {}'.format(len(graph_complete_odd.nodes())))
        print('Number of edges (odd): {}'.format(len(graph_complete_odd.edges())))
    odd_matching_edges = nx.algorithms.max_weight_matching(graph_complete_odd, True)
    if verbose: print('Number of edges in matching: {}'.format(len(odd_matching_edges)))
    multi_graph = create_new_graph(graph, odd_matching_edges)

    return(create_eulerian_circuit(multi_graph, starting_node))

def idx_from_figures(*args):
    dicx = []
    for n in range(len(args)):
        tmp = []
        for i in range(len(args[n])):
            tmp.append(args[n][i].split('/')[-1].split('.')[-2])
        dicx.append(dict(zip(tmp,np.linspace(0,len(args[n])-1,len(args[n]),dtype=int))))
    return(dicx)

def figures_from_idx(*args):
    dicx = []
    for n in range(len(args)):
        tmp = []
        for i in range(len(args[n])):
            tmp.append(args[n][i].split('/')[-1].split('.')[-2])
        dicx.append(dict(zip(np.linspace(0,len(args[n])-1,len(args[n]),dtype=int),tmp)))
    return(dicx)


# ## Build dictionary of gestures

# read dynamic score library
register = np.array(glob.glob('./FIGURES/REGISTER/*'))
dynamics = np.array(glob.glob('./FIGURES/DYNAMICS/*'))
lines = np.array(glob.glob('./FIGURES/LINES/*'))
gestures = np.array(glob.glob('./FIGURES/GESTURES/*'))

idxgest,idxdyn,idxreg,idxlin = idx_from_figures(gestures,dynamics,register,lines)

# full colors
ldx = []
ddx = []
rdx = []
for i in range(len(gestures)):
    ldx.append(np.linspace(0,len(lines)-1,len(lines),dtype=int))
    ddx.append(np.linspace(0,len(dynamics)-1,len(dynamics),dtype=int))
    rdx.append(np.linspace(0,len(register)-1,len(register),dtype=int))

# select particular combinations when needed
selection = {
    'JW'  : [['null'],[None],['crescendo','decrescendo','null']],
    'St'  : [[None],[None],['decr-nulla','legato','crescendo','arpeggio','decrescendo','nulla-cresc','null']],
    'BRH' : [['null'],[None],['decr-nulla','legato','crescendo','decrescendo','nulla-cresc','null']],
    'KSC' : [['low'],[None],['null']],
    'KC'  : [['low'],['p','f'],['null']],
    'NH'  : [['low'],[None],[None]],
    'TP'  : [[None],[None],['crescendo','arpeggio','decrescendo','null']],
    'MH'  : [['low'],['sfz'],['null']],
    'WT'  : [['high'],['ppp'],['legato','null']],
    'KSO' : [['low'],[None],['null']]
}
for n in list(selection.keys()):
    if selection[n][0][0] != None: rdx[idxgest[n]] = np.array([idxreg[n] for n in selection[n][0]])
    if selection[n][1][0] != None: ddx[idxgest[n]] = np.array([idxdyn[n] for n in selection[n][1]])
    if selection[n][2][0] != None: ldx[idxgest[n]] = np.array([idxlin[n] for n in selection[n][2]])

gdict = []
for i in list(idxgest.values()):
    gdict.append(dict([
        ('gesture',gestures[i]),
        ('register',dict(zip(rdx[i],register[rdx[i]]))),
        ('dynamics',dict(zip(ddx[i],dynamics[ddx[i]]))),
        ('lines',dict(zip(ldx[i],lines[ldx[i]])))
    ]))

performance = {
    'FR': 'fast runs' ,
    'KC': 'key click (no air)',
    'FPB': 'fast bitch bending , or alternatively, enharmonic trill',
    'JW': 'jet whistle',
    'FT': 'fluttertongue',
    'St': 'staccato',
    'BRH': 'air sound',
    'Tr#': 'semitone trill up',
    'Trb': 'semitone trill down',
    'KSC': 'key slap (closed embouchure) – with air',
    'AT':  'double tonguing', # should be DT
    'Tr2': '“Sciarrino trill”: play a fast trill on D/D# with the right hand while\
            fingering a note with the left hand',
    'Tr':  'tone trill',
    'StT': 'accent', # should be Acc
    'MF':  'multi-phonics by fingering',
    'StA': 'staccato+accent', # change symbol
    'NH':  'natural harmonics',
    'TP':  'tongue pizzicato',
    'MH':  'multi-phonics by overblown harmonics',
    'WVU': 'with voice higher than played pitch',
    'Reg': 'pitched sound (with or without noise)',
    'WV':  'with voice at played pitch',
    'WT':  'whistle tone', 
    'WVD': 'with voice lower than played pitch',
    'KSO': 'key slap (open embouchure) – with air',
    'ETr': 'triple tonguing (very fast)'} # should be TrT

# ### Input parameters

Sections = {
    'Section 1'  : {'gest' : ['FPB','Tr2','ETr','FPB', 'Reg', 'Reg','FPB','Tr2','FPB',
                              'Tr2', 'Reg','ETr', 'Reg','ETr','Tr2','ETr','FPB'], 
                    'totgest' : None },
    'Section 2'  : {'gest' : ['Reg','FT','Tr2','Tr','FPB','St','Tr','FT',
                              'Tr','St','FPB','St','Tr','FT','FPB','Tr2','ETr',
                              'Reg','FT','FT','Tr2','Reg','FPB','ETr','FPB','Tr', 'Reg',
                              'ETr', 'Reg','FT', 'Reg','FPB','St','Reg','Reg','Reg'], 
                    'totgest' : None },
    'Section 3'  : {'gest' : ['ETr','StT','MH', 'Reg','ETr', 'Reg','St','MH','ETr',
                              'ETr','FR','FPB', 'Reg','FR','FT','FR','FPB','ETr',
                              'ETr','FPB','MH','Tr2','FR','FPB','StT','Tr2','FPB','Tr2',
                              'Reg','MH','Tr2', 'Reg','FT','Tr2','StT','Tr','FT','Tr2','FPB',
                              'Tr','Tr','FT','St', 'Reg','Tr','StA','Tr','MH','St','Tr2','WV',
                              'WVU','WVD','StT','WV','WVU','WVD','ETr'], 
                    'totgest' : None},
    'Section 4'  : {'gest' : ['Tr2','St','WV','WVU','WVD','FT','Trb','StA', 'Reg','Tr','StT',
                              'FR','ETr','St','Tr#','FR', 'Reg','WV','WVU','WVD','Tr2','FT',
                              'WV','WVU','WVD','AT','StT','Trb','StT','Tr','Tr2','FPB','MH',
                              'MH','StT','NH','FR','Tr','MH','StA','AT','FR','MH','FR','MH',
                              'MH','Tr2','FR','FPB','MH','FR','StA','Trb', 'Reg','Tr2','NH','St',
                              'Tr2','MH','Tr2','FPB','Tr2'], 
                    'totgest' : None},
    'Section 5'  : {'gest' : ['Tr2','WV','WVU','WVD','MH','Tr2','Trb','BRH','WV','WVU','WVD',
                              'WV','WVU','WVD','FT','FPB','WV','WVU','WVD','Trb','BRH','FPB',
                              'Trb','NH','Reg','AT','StT','FR','JW', 'StT','FR','FR','JW','ETr',
                              'St','FR','Tr2','MH','MH','St','Tr','FT','FR','MH','FPB','MH',
                              'Tr','Trb','TP','KC','FPB', 'KC','AT','TP','StA','FR','StT','WV','WVU','WVD',
                              'StT', 'ETr','FT','FR','StT','StA','StT'], 
                    'totgest' : None},
    'Section 6'  : {'gest' : ['Tr2', 'WV','WVU','WVD', 'MH', 'Tr2', 'Trb', 'BRH', 'WV','WVU','WVD',
                              'WV','WVU','WVD', 'FT', 'FPB', 'WV','WVU','WVD', 'Trb', 'BRH', 'FPB', 'Trb', 
                              'Reg', 'StT', 'FR','AT', 'JW', 'StT', 'FR', 'FR', 'WV','WVU','WVD', 'JW', 'ETr',
                              'St', 'FR', 'WV', 'Tr2', 'MH', 'MH', 'StA', 'WV', 'Tr', 'FT','NH',
                              'FR', 'WV','WVU','WVD', 'MH','AT', 'FPB', 'MH', 'Tr', 'Trb', 'TP', 'KC', 
                              'WV','WVU','WVD', 'FPB', 'KC', 'TP', 'StA', 'FR', 'StT', 'WV','WVU','WVD', 
                              'StT', 'ETr', 'FT', 'FR', 'StT', 'St', 'StA'], 
                    'totgest' : None},
    'Section 7'  : {'gest' : ['Reg','KC','KSC','KSO','BRH','TP','ETr','BRH','KC','KSC','Trb',
                              'ETr','Trb','KSC','MF','TP','KC','WV','WVU','WVD','JW', 'Reg','KSO','JW',
                              'ETr','NH','FPB','NH','AT','KSC','Tr','KC','BRH','ETr','Tr#',
                              'Reg','FPB','KC','Tr2','FR','FPB','WT','WV','WVU','WVD','MH','NH', 'Reg',
                              'JW','Tr#','JW','KSO','FPB','KSC','AT','KSO','KSC', 'Reg','FT','StT', 'St',
                              'KC','KC','KC','FR','Tr','TP','KSO','FR','St','WT','MH', 'StA',
                              'WT','KSC','FR','TP','FR','MF','FR','StT', 'St', 'StA','FR','WT', 'Reg'], 
                    'totgest' : None},
    'Section 8'  : {'gest' : ['MH','Tr2','ETr','KSC','ETr','FPB','Tr2','KSC',
                              'JW','KSC','FPB','JW','BRH','StT','NH','FR','BRH',
                              'KC','WV','WVU','WVD','KSC','MH','Tr2','AT','St','MF','BRH',
                              'WV','WVU','WVD','Tr','MH','KSO','MH','MF','FPB','KC',
                              'TP','KSO','TP','WT','MH','NH','TP','FPB',
                              'WV','WVU','WVD','NH','TP','MF','St','FT','AT','WV','WVU','WVD','FT',
                              'KC','KSO','WV','WVU','WVD','MF','KSO','WT','KSO','MH'], 
                    'totgest' : None},
    'Section 9'  : {'gest' : ['JW','WV','WVU','WVD','NH','JW','FR','FT','JW','WT',
                              'KSC','BRH','FT','BRH','JW','ETr','JW','KSC',
                              'Tr','BRH','WT','JW','MF','Tr2','TP','FR',
                              'JW','WT','KC','JW','Tr','WT','WT',
                              'KSO','JW','KSO','BRH','AT','Tr2','TP',
                              'Tr','FR','KC','JW','TP','WT','KC',
                              'Tr','KC','Tr','TP','AT','TP','JW'], 
                    'totgest' : None},
    'Section 10' : {'gest' : ['BRH','KSO','KSC','MF','TP','Tr2','KC',
                              'KSC','KSO','KC','JW','KC','WT','KSC',
                              'FR','BRH','JW','KC','NH','BRH','KSC',
                              'WT','TP','KC','WV','WVU','WVD','TP','WV','WVU','WVD','BRH',
                              'FR','KC','TP','TP','BRH','WT',
                              'JW','BRH','TP','JW','TP',
                              'KC','BRH','NH','BRH'],
                    'totgest' : None},
    'Section 11' : {'gest' : ['WT','BRH','KC','WT','KC','MF','KC','WT','MF','WT','KC','BRH','WT',
                              'BRH','WT','MF','WT'], 
                    'totgest' : None}
}

ngest = len(Sections[sec]['gest'])
if Sections[sec]['totgest'] == None:
    totgest = ngest
else:
    totgest = Sections[sec]['totgest']

files = glob.glob('./FIGURES/COMPOUNDED/*.svg')
for f in files:
    os.remove(f)

glist = [idxgest[n] for n in Sections[sec]['gest']]
random.shuffle(glist)

for t in range(totgest):
    n = glist[t%ngest]
    tmp = st.fromfile(gdict[n]['gesture'])
    r = random.sample(range(len(rdx[n])),1)
    tmp.append(st.fromfile(gdict[n]['register'][rdx[n][r[0]]]))
    r = random.sample(range(len(ddx[n])),1)
    tmp.append(st.fromfile(gdict[n]['dynamics'][ddx[n][r[0]]]))
    r = random.sample(range(len(ldx[n])),1)
    tmp.append(st.fromfile(gdict[n]['lines'][ldx[n][r[0]]]))
    tmp.save('./FIGURES/COMPOUNDED/'+str(t)+'.svg')

final = glob.glob('./FIGURES/COMPOUNDED/*')
idx = np.linspace(0,totgest-1,totgest,dtype=int)
finaldict = dict(zip(idx,final))


# ### Build the progression of gestures as a Eulerian circuit on a network

if nxmodel == 'BA':
    Gx = nx.barabasi_albert_graph(totgest,2)
if nxmodel == 'DBA':
    Gx = nx.dual_barabasi_albert_graph(totgest,2,1,0.5)
elif nxmodel == 'WS':
    Gx = nx.watts_strogatz_graph(totgest,2,0.2)
elif nxmodel == 'NWS':
    Gx = nx.newman_watts_strogatz_graph(totgest,2,0.2)
elif nxmodel == 'ER':
    # use with caution: the length of the Eulerian path tends to be VERY high
    Gx = nx.erdos_renyi_graph(totgest,0.05,directed=True)

chino = chinese_postman(Gx,3,verbose=False)
seq = [chino[0][0]]
for s in range(1,len(chino)):
    seq.append(chino[s][1])
print('length of the path = ',len(seq))

section = []
for i in seq:
    section.append(finaldict[i])

tmp = []
for n in range(len(seq)):
    tmp.append([[section[n]]])
enodes = pd.DataFrame(tmp,columns=['Label'])

df = np.asarray(enodes)
dff,idx = np.unique(df,return_inverse=True)
tmp = []
for n in range(dff.shape[0]):
    tmp.append(dff[n])
enodes = pd.DataFrame(tmp,columns=['Label'])

tmp = []
for n in range(1,len(seq)):
    tmp.append([str(idx[n-1]),str(idx[n]),1])
eedges = pd.DataFrame(tmp,columns=['Source','Target','Weight'])

# engine = 'neato'
engine = 'dot'
# engine = 'fdp'
# engine = 'circo'
# engine = 'twopi'
# engine = 'patchwork'

G = Digraph(engine=engine,format='svg')

G.attr(rankdir='LR',ratio='0.647',size='17,17',pad='0.2',splines='ortho',overlap='false',mode='KK')
G.attr('graph',label=str(sec),fontname='Helvetica Neue',fontsize='32',labelloc='t')
G.attr('node', shape='square',pad='0.2',fontname='Helvetica Neue',fontsize='16')
G.attr('edge',dir='forward',arrowtype='empty',arrowsize='0.5')

df = eedges

nodelist = []
for idx, row in df.iterrows():
    node1, node2, weight = [str(i) for i in row]

    if node1 not in nodelist:
        G.node(node1)
        nodelist.append(node1)
    if node2 not in nodelist:
        G.node(node2)
        nodelist.append(node2)

    G.edge(node1,node2)

for g in nodelist:
    G.node(str(g),label='',image='.'+finaldict[int(g)])
    
G.render('./SECTIONS/'+sec,view=True)

# ### Linearized score version

# linearized version
engine = 'patchwork'

G = Digraph(engine=engine,format='svg')

G.attr(rankdir='LR',ratio='0.647',size='17,17',pad='0.2',splines='ortho',overlap='false',penwidth='0')
G.attr('graph',label=str(sec),fontname='Helvetica Neue',fontsize='32',labelloc='t')
G.attr('node', shape='square',pad='0.2',fontname='Helvetica Neue',fontsize='16')
G.attr('edge',dir='forward',arrowtype='empty',arrowsize='0.5')

for i,idx in enumerate(seq):
    G.node(str(i),label='',image='.'+finaldict[int(idx)])
    
G.render('./SECTIONS/'+sec+' linear',view=True)

# Sections 0 ad 12 
if sec == 'Section0-12':
    engine = 'dot'
    G = Digraph(engine=engine,format='svg')
    
    G.attr(rankdir='LR',ratio='0.657',size='17,17',pad='0.2',splines='ortho')
    G.attr('graph',fontname='Helvetica Neue',fontsize='32',labelloc='t',nodesep='0.05')
    G.attr('node', shape='square',pad='0.2',fontname='Helvetica Neue',fontsize='16')
    G.attr('edge',arrowtype='empty')
  
    G.node('0',label='SILENCE\n DARK',)
    G.render('./SECTIONS/'+sec,view=True)




