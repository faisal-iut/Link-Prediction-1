import igraph
import pandas as pd
import numpy as np
import time
from model import Data
import math
PREDICT = "randomprediction.csv"

prediction94453 = pd.read_csv("prediction94453", header=0, index_col=0)
prediction94416 = pd.read_csv("prediction94416", header=0, index_col=0)
prediction94410 = pd.read_csv("prediction94410", header=0, index_col=0)
prediction = pd.concat([prediction94453, prediction94416, prediction94410], axis=1)
prediction[(prediction["prediction94453"] != prediction["prediction94416"]) + (prediction["prediction94453"] != prediction["prediction94410"]) + (prediction["prediction94416"] != prediction["prediction94410"])]

ans = pd.DataFrame(np.int_(np.rint(np.mean(prediction, axis=1))))

predict = pd.read_csv(PREDICT, sep=",")
predict["prediction"] = ans
predict.to_csv("prediction", index=False)
pd.DataFrame(s_train).to_csv("s_train", index=True)
pd.DataFrame(s_test).to_csv("s_test", index=True)

data = Data(sample=True)
data.load_data()

data.sample(prop=1, load=True)

data.get_node_dict()
data.prepare_data(delete=False)
data.init_graph_paper()
data.init_graph_author()


def get_year(ids, return_type="graph_id"):
    # need self.id_graphid
    # input: int: id1 and id2
    # output: tuple: (from_graph_id, to_graph_id) or (from_id, to_id)
    # year(from_id) >= year(to_id)

    year_id1 = data.node_dict[ids[0]]["year"]
    year_id2 = data.node_dict[ids[1]]["year"]
    if return_type == "graph_id":
        if year_id1 >= year_id2:  # TODO: how to deal with papers in same year, I ignore it now
            return year_id1-year_id2
        else:
            return year_id1-year_id1

dyear = data.data_train_positive[["id_source", "id_target"]].apply(get_year, axis=1)

dyear.value_counts()

# matrix = data.graph_paper.similarity_inverse_log_weighted(mode="ALL")


def similarity(ids, graph, method= "adamic_adar", direct=False):
    if direct:
        pass
    else:
        i = data.id_graphid_paper[ids[0]]
        j = data.id_graphid_paper[ids[1]]
    if method == "adamic_adar":
		return sum([1.0/math.log(graph.degree(v)) for v in set(graph.neighbors(i)).intersection(set(graph.neighbors(j)))])

t0 = time.clock()
features_adamic_adar_paper = data.data_train[["id_source", "id_target"]].iloc[0:10000].apply(similarity, args=(data.graph_paper,),
                                                                          axis=1)
print(time.clock() - t0)
similarity(data.graph_paper, i=1001, j=1002, method ="adamic_adar")


def get_authors_list():
    authors_list = []

    for key, value in data.node_dict.items():
        if type(value['tkzd_author']) == list:
            authors_list.extend(value['tkzd_author'])

    authors_list = list(set(authors_list))
    authors_list.remove('')
    return authors_list

def init_graph_author():
    authors_list = get_authors_list()
    graph_author.add_vertices(authors_list)

    for i in range(graph_author.vcount()):
        id_graphid_author[graph_author.vs["name"][i]] = i


def author_citation_edge(ids):
    citation_list = []
    graphids = data.get_direct(ids, graphtype="author", return_type="id")
    from_authors = data.node_dict[graphids[0]]['tkzd_author']
    to_authors = data.node_dict[graphids[1]]['tkzd_author']
    if type(from_authors)==list and type(to_authors)==list:
        for from_a in from_authors:
            for to_a in to_authors:
                if from_a != '' and to_a != '':
                    citation_list.append((id_graphid_author[from_a], id_graphid_author[to_a]))
        return citation_list
    else:
        return np.nan




print("Calculating the feature")
t0 = time.clock()
author_citation_edges = data.data_train_positive[["id_source", "id_target"]].apply(author_citation_edge, axis=1)
print(time.clock() - t0)
list_citation_edges = author_citation_edges.tolist()
list_citation_edges = [x for x in list_citation_edges if str(x) != "nan"]
list_citation_edges = [y for x in list_citation_edges for y in x]

graph_author.add_edges(list_citation_edges)

t0 = time.clock()
modified_data_train = pd.concat([pd.DataFrame([{"id_source":201080, "id_target":9905149}]), data.data_train[["id_source", "id_target"]]])    # TODO: need automation
training_citation_edges = modified_data_train.apply(author_citation_edge, axis=1)
training_citation_edges = training_citation_edges.iloc[1:]
print(time.clock() - t0)

def AciteB(edge):
    neighbors = graph_author.neighbors(graph_author.vs[edge[0]], mode="OUT")    # get neighbors of from_author
    length = neighbors.count(edge[1])
    return(length)

def meanAciteB(input_list):
    # input)list: e.g. [(123,456), (234,252)]
    if type(input_list) == list:
        acitebs = list(map(AciteB, input_list))
        return np.mean(acitebs)
    else:
        return 0

t0 = time.clock()
feature_meanAciteB = training_citation_edges.apply(meanAciteB)
print(time.clock() - t0)
feature_meanAciteB[data.data_train["predict"]==1] -= 1
feature_meanAciteB[feature_meanAciteB==-1] = 0

t0 = time.clock()
modified_data_test = pd.concat([pd.DataFrame([{"id_source":9912290, "id_target":7120}]), data.data_test[["id_source", "id_target"]]])    # TODO: need automation
testing_citation_edges = modified_data_test.apply(author_citation_edge, axis=1)
testing_citation_edges = testing_citation_edges.iloc[1:]
print(time.clock() - t0)

t0 = time.clock()
test_feature_meanAciteB = testing_citation_edges.apply(meanAciteB)
print(time.clock() - t0)



#
# graph_author.write_picklez(fname="graph_author")
# Read_Pickle(klass, fname=None)


#
#
# data.init_graph()
#
# data.graph_paper
#
# data.graph_paper.pagerank()
#
# data.graph_paper.similarity_dice(vertices=(10327, 25399), mode="OUT", loops=False)
#
#
# #def
#
#
#
# def get_graph_simi(ids, train=True):
#     # ids is from data.data_train[["id_source", "id_target"]].apply(..., axis=1)
#     graphids = data.get_direct(ids)
#     # graphid_from = graphids[0]    # from
#     graphid_to = graphids[1]    # to
#     # if the training observation has connection, we need delete it first.
#     if train:
#         # num_edge = data.graph.get_eid(v1=graphid_from, v2=graphid_to, directed=False, error=False)
#         # if num_edge != -1:
#         #     # delete edge
#         #     data.graph.delete_edges([(graphid_from, graphid_to)])
#         graphid_in = pd.Series(data.graph_paper.neighbors(graphid_to, mode="IN"))
#         simi_dice_in = graphid_in.apply(simi_dice, args=(graphid_to,))
#         # if num_edge != -1:
#         #     # add edge back
#         #     data.graph.add_edges([(graphid_from, graphid_to)])
#         return np.mean(simi_dice_in)
#     else:
#         graphid_in = pd.Series(data.graph_paper.neighbors(graphid_to, mode="IN"))
#         simi_dice_in = graphid_in.apply(simi_dice, args=(graphid_to,))
#         return np.mean(simi_dice_in)
#
#
# def get_graph_simi(ids, train=True):
#     # ids is from data.data_train[["id_source", "id_target"]].apply(..., axis=1)
#     graphids = data.get_direct(ids)
#     graphid_from = graphids[0]
#     graphid_to = graphids[1]
#     # if the training observation has connection, we need delete it first.
#     if train:
#         # num_edge = data.graph.get_eid(v1=graphid_from, v2=graphid_to, directed=False, error=False)
#         # if num_edge != -1:
#         #     # delete edge
#         #     data.graph.delete_edges([(graphid_from, graphid_to)])
#         graphid_in = pd.Series(data.graph_paper.neighbors(graphid_to, mode="IN"))
#         simi_dice_in = graphid_in.apply(simi_dice, args=(graphid_from,))
#         # if num_edge != -1:
#         #     # add edge back
#         #     data.graph.add_edges([(graphid_from, graphid_to)])
#         return np.mean(simi_dice_in)
#     else:
#         graphid_in = pd.Series(data.graph_paper.neighbors(graphid_to, mode="IN"))
#         simi_dice_in = graphid_in.apply(simi_dice, args=(graphid_from,))
#         return np.mean(simi_dice_in)
#
# def get_graph_simi(ids):
#     # ids is from data.data_train[["id_source", "id_target"]].apply(..., axis=1)
#     graphids = data.get_direct(ids)
#     graphid_from = graphids[0]
#     graphid_to = graphids[1]
#
#     graphid_in = pd.Series(data.graph_paper.neighbors(graphid_to, mode="IN"))
#     simi_dice_in = graphid_in.apply(simi_dice, args=(graphid_from,))
#     return np.mean(simi_dice_in)
#
# def simi_dice(graphid_in, graphid_from):
#     # calculate
#     simi_dice = data.graph_paper.similarity_jaccard(vertices=(graphid_in, graphid_from), mode="OUT", loops=False)[0][1]
#     return simi_dice
#
# data.data_train[["id_source", "id_target"]].iloc[0:1000].apply(get_graph_simi, axis=1)
#
#
# t0 = time.clock()
# test = data.data_train[["id_source", "id_target"]].apply(get_graph_simi, axis=1)
# print(time.clock() - t0)    # 1.160415999999998 sec
#
# #
# # edges.tolist()
# #
# # g=igraph.Graph(directed=True)
# #
# #
# # data.graph.add_edges([(9905020, 9310158)])
# #
# # g.add_vertices(list(data.node_dict.keys()))
# # g.add_edges(edges.tolist())
# # g.add_edges([('204235', '9812066'),('9905020', '9310158')])
# #
# # id_graphid= {}
#
# # for i in range(data.node_dict.__len__()):
# #     id_graphid[g.vs["name"][i]] = i
