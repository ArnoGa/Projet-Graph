# https://networkx.org/documentation/stable/tutorial.html
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt

# build_graph :
# - input : a boolean to indicate if you want a directed graph
# - output : a directed graph if di=True & a non-directed if di=False


def build_graph(di):
    Data = open("followers.csv", 'r')
    next(Data, None)  # skip first line

    if di:
        Graphtype = nx.DiGraph()
    else:
        Graphtype = nx.Graph()

    G = nx.read_edgelist(Data,
                         delimiter=",",
                         create_using=Graphtype,
                         nodetype=int,
                         data=False)

    return G

# num_comp :
# - input : a undirected graph
# - output : the number of component in this graph
# - note : we use a alternated version of DFS to count the number of component


def num_comp(G):
    n_component = 0
    queue = []
    for node in G.nodes():
        if len(G.nodes[node]) == 0:
            n_component += 1
            G.nodes[node]['comp'] = n_component
            queue = list(G.adj[node])

            while len(queue) > 0:
                popped = queue.pop(0)
                if len(G.nodes[popped]) == 0:
                    G.nodes[popped]['comp'] = n_component
                    for sub_nei in G.adj[popped]:
                        if (len(G.nodes[sub_nei]) == 0):
                            queue.append(sub_nei)

    return n_component


tot_bridge = 0
time = 0

# num_bridge :
# - input : a undirected graph
# - output : the number of bridge in this graph
# - note : this fonction init the paramet for the graph & call the function "bridge_det" on each unvisited nodes


def num_bridges(G):
    for node in G.nodes():
        G.nodes[node]['visited'] = False
        G.nodes[node]['disc'] = float("Inf")
        G.nodes[node]['low'] = float("Inf")
    for node in G.nodes():
        if G.nodes[node]['visited'] == False:
            bridge_det(node)

# bridge_det :
# - input : a node of a graph
# - output : none
# - note : recursive function to count bridge, based on a DFS


def bridge_det(node):
    global time
    global tot_bridge
    children = 0
    G.nodes[node]['visited'] = True
    G.nodes[node]['disc'] = time
    G.nodes[node]['parent'] = -1
    G.nodes[node]['low'] = time
    time += 1
    for nei in G.adj[node]:
        if G.nodes[nei]['visited'] == False:
            G.nodes[nei]['parent'] = node
            children += 1
            bridge_det(nei)
            G.nodes[node]['low'] = min(
                G.nodes[nei]['low'], G.nodes[node]['low'])
            if G.nodes[nei]['low'] > G.nodes[node]['disc']:
                tot_bridge += 1
        elif nei != G.nodes[node]['parent']:
            G.nodes[node]['low'] = min(
                G.nodes[node]['low'], G.nodes[nei]['disc'])

# numLocalBridge
# input : a undirected graph (Graph)
# output number of local bridges (int)
# node : take a graph and for each neighboors of each node, calculate if there is a local bridge between the two


def numLocalBridge(G):
    n_local_bridge = 0
    for nodes in G.nodes:
        adj_a = set(G.adj[nodes])
        for b in adj_a:
            adj_b = set(G.adj[b])
            # if there is no commun elements between the neighboor-
            if not adj_a.intersection(adj_b):
                # -of the node and the neighboors of the neighboor there is a local bridge between the two
                n_local_bridge += 1

    # we divide by two because it finds the bridge in two way, (e.g. bridge(1,2) and (2,1) are the same)
    return n_local_bridge // 2

# init_pg :
# - input : a directed a graph
# - output : a directed a graph initialize with variable use in pagerank()


def init_pg(G):
    node_num = G.number_of_nodes()
    for node in G.nodes:
        # setup des données utiliser par pagerank
        G.nodes[node]['pg'] = 1/node_num
        G.nodes[node]['new_pg'] = 0
        G.nodes[node]['id'] = node
    return G

# pagerank :
# - input : G - a directed a graph & k - the number of loop for the pagerank
# - output : the directed graph G, with the value of pagerank in the parameters of the nodes
# - note : it's the simple pagerank algorithm without teleportation


def pagerank(G, k):
    if k == 0:
        return G

    total = 0
    for node in G.nodes:
        given_pg = 0
        if len(G.adj[node]) > 0:
            given_pg = G.nodes[node]['pg']/len(G.adj[node])
        else:
            G.nodes[node]['new_pg'] += G.nodes[node]['pg']
        for adj in G.adj[node]:
            G.nodes[adj]['new_pg'] += given_pg

    for node in G.nodes:
        G.nodes[node]['pg'] = G.nodes[node]['new_pg']
        G.nodes[node]['new_pg'] = 0
    pagerank(G, k-1)

# findmax20 :
# - input : G a directed graph on which we have applied pagerank
# - output : a list of the top 20 pagerank influencers and their number of shots


def findmax20(G):
    designersCSV = pd.read_csv('designers.csv')
    shotsCSV = pd.read_csv('shots.csv')
    find_max = []
    for node in nx.nodes(BDG):
        find_max.append((nx.nodes(BDG)[node]))
    sortedlist = (sorted(find_max, key=lambda a: a["pg"], reverse=True)[:20])
    for user in sortedlist:
        user['location'] = "unknown"
        user['to_li'] = 0
        user['av_li'] = 0
        user['shots'] = 0
        for row in designersCSV.itertuples():
            user_id = row[1]
            localtion = row[2]
            if user['id'] == user_id:
                if row[2] == "  null":
                    localtion = "  unknown"
                user['location'] = localtion
                break
        for row in shotsCSV.itertuples():
            user_id = row[1]
            likes = row[3]
            if user['id'] == user_id:
                user['shots'] += 1
                user['to_li'] += row[3]
        if (user['shots'] > 0):
            user['av_li'] = user['to_li'] / user['shots']
        else:
            user['av_li'] = user['to_li']

    return sortedlist


triadic_list = []
timestamp_list = []
location_list = []
flatten_location = []


# triadic_closure :
# - input : G ( graph )
# - output : number of triadic closure (int)
# - note : to find triadic closure we check if 2 nodes have other nodes in common
def triadic_closure(G):
    n_tria_clo = 0
    for a in G.nodes:
        adj_a = G.adj[a]
        for b in adj_a:
            adj_b = G.adj[b]
            intersection = [inter for inter in adj_b if inter in adj_a]
            for common in intersection:
                triad = sorted([a, b, common])
                if triad not in triadic_list:
                    triadic_list.append(triad)
                    t_list = sorted([G.edges[a, b]['timestamp'], G.edges[a, common]
                                    ['timestamp'], G.edges[b, common]['timestamp']])
                    print("the friendship between {}, {} and {} takes {} seconds".format(
                        a, b, common, (t_list[2] - t_list[1])))
                    timestamp_list.append((t_list[2] - t_list[1]))
                    n_tria_clo += 1
    return n_tria_clo


# triadic_year_after_year :
# - input (null)
# - output (null) but modifie flatted_location, a list used for the plot
# - note : find and put in the  Standard output every triadic closure created year after year.
def triadic_year_after_year():
    followerCSV = pd.read_csv('followers.csv')
    # followerCSV = pd.read_csv('mydb.csv')
    last_follow = 1513617975
    first_follow = 1264283835
    one_year_in_sec = 31536000
    time = first_follow
    G = nx.Graph()
    n_tria_clo = 0
    for i in range(9):
        for row in followerCSV.itertuples():
            uid_src = row[1]
            uid_dst = row[2]
            timestamp = row[3]
            if timestamp < time and (uid_src in list_BDG):
                G.add_node(uid_src)
                G.add_node(uid_dst)
                G.add_edge(uid_src, uid_dst, timestamp=timestamp)
        n_tria_clo += triadic_closure(G)
        print("number of triadic closure : {} with {} nodes ({} year(s))".format(
            n_tria_clo, G.number_of_nodes(), i))
        time += one_year_in_sec
    designersCSV = pd.read_csv('designers.csv')
    for triad in triadic_list:
        for uid in triad:
            for row in designersCSV.itertuples():
                if row[1] == uid:
                    flag = False
                    for city in location_list:
                        if row[2] == city[0]:
                            city[1] += 1
                            flag = True
                            break
                    if flag == False:
                        location_list.append([row[2], 1])
                    break
    top20 = sorted(location_list, key=lambda a: a[1], reverse=True)[:20]

    for city in top20:
        for i in range(city[1]):
            flatten_location.append(city[0])


# find_av_loc
# - input (null) but use results from previous function
# - output (null) but print the average time of friendship for each city
# - note : for every triadic closure, calculate the average time difference of locations ( if they the 3 users live in the same place )
def find_av_loc():
    designersCSV = pd.read_csv('designers.csv')
    average_friendship_time = {}
    three_city = ["a", "b", "c"]
    for i in range(len(triadic_list)):
        triad = triadic_list[i]
        three_city = []
        for uid in triad:
            for row in designersCSV.itertuples():
                if row[1] == uid:
                    # if the userID correspond to the userID of the designers CSV, we add the city to the list
                    three_city.append(row[2])
                    break
        if three_city[0] == three_city[1] == three_city[2]:
            if three_city[0] not in average_friendship_time:
                average_friendship_time[three_city[0]] = [timestamp_list[i], 1]
            else:
                average_friendship_time.update({three_city[0]: [
                    average_friendship_time[three_city[0][0]]+timestamp_list[i], average_friendship_time[three_city[0][1]]+1]})
    for city in average_friendship_time:
        print("the average friendship time in {} is {} secondes with {} triangles".format(
            city, average_friendship_time[city][0]/average_friendship_time[city][1], average_friendship_time[city][1]))


# -------- Function Call -------------

print("start")


# Question 1

G = build_graph(False)

print("my number of components : " + str(num_comp(G)))

num_bridges(G)
print("my number of bridges : " + str(tot_bridge))

print("my number of local_bridges : " + str(numLocalBridge(G)))

Dir_G = build_graph(True)
list_BDG = max(nx.weakly_connected_components(Dir_G), key=len)
BDG = Dir_G.subgraph(list_BDG)

# Question 2

init_pg(BDG)
pagerank(BDG, 10)
print('pagerank calcul finish')
for node in findmax20(BDG):
    print("user {} has a pagerank of {}, a total likes of {} with a average of {} with a total of {} shots. He lives in{}".format(
        node["id"], node["pg"], node['to_li'], node['av_li'], node['shots'], node['location']))

# Question 3

triadic_year_after_year()

fig = plt.figure()
fig.subplots_adjust(top=0.8)
ax1 = fig.add_subplot(222)
ax1.set_ylabel('percentage')
ax1.set_xlabel('third friendship in seconds')
ax1.set_title('histogramme of friendship')
ax1.hist(timestamp_list)

ax2 = fig.add_subplot(223)
ax2.set_ylabel('number')
ax2.set_xlabel('location')
ax2.set_title('top 20 location')
ax2.hist(flatten_location)

plt.show()

find_av_loc()
