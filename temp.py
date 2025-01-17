
###############################################
import pickle
import time
from audioop import reverse
from sklearn.metrics.pairwise import euclidean_distances
from hyperopt import fmin, tpe, hp, STATUS_OK,Trials,trials_from_docs
import numpy as np
import random
from scipy import stats
import pandas as pd
from sklearn.cluster import KMeans
import random

# def objective(args):
#     x= args
#     print("X is {} and loss is {}".format(x,x[0] ** 2))
#     return {'loss': x[0] ** 2, 'status': STATUS_OK }
#
#
# space  = [hp.uniform('x',-10,10)
# ]
# # trial = Trials()
# trial = pickle.load(open("trial_16_outof100.p",'rb'))
#
# best,trials_new = fmin(objective,
#     space=space,
#     algo=tpe.suggest,
#     max_evals=116,
#     trials=trial,
#     rstate=np.random.RandomState(10),
#
#                        )
#
# print(best)
# pickle.dump(trials_new, open('trial_100_16initial.p', 'wb'))
#################################################################
from datetime import timedelta
from matplotlib import pyplot as plt
import matplotlib
def find_n_initial(trial, N, good, bad):
    """
    This method sort, first the bad points and then the good points and works better than the Vs the reverse one.
    """
    losses = trial.losses()
    losses = [abs(i) for i in losses]
    losses = np.array(losses)
    losses_index = np.argsort(losses)

    losses_index = list(losses_index)
    losses = list(losses)

    selected_list = []
    for i, v in enumerate(losses_index):
        if i >= N:
            break
        else:
            if i < N - good:
                selected_list.append(v)
            else:
                Bests = losses_index[-good:]
                selected_list = selected_list + Bests
                break

    new_trial = []
    for i in selected_list:
        new_trial.append(trial.trials[i])

    empty_trial = Trials()
    trial_merged = trials_from_docs(list(empty_trial) + new_trial)

    for i, v in enumerate(trial_merged.trials):

        need_to_change = trial_merged.trials[i]['tid']

        trial_merged.trials[i]['tid'] = i
        trial_merged.trials[i]['misc']['tid'] = i
        for key in v['misc']['idxs']:
            if v['misc']['idxs'][str(key)] == [need_to_change]:
                trial_merged.trials[i]['misc']['idxs'][str(key)] = [i]
    return trial_merged


def find_n_initial1(trial, N, good, bad):
    '''
    This method sort the trial based on, good points.
    it means it picks the goods first and then the rest(bads), slower in compare the another version
    '''

    losses = trial.losses()
    losses = [abs(i) for i in losses]
    losses = np.array(losses)
    losses_index = np.argsort(losses)

    losses_index = np.flip(losses_index)

    losses_index = list(losses_index)
    losses = list(losses)

    selected_list = []

    for i, v in enumerate(losses_index):
        if i >= N:
            break
        else:
            if i < N - bad:
                selected_list.append(v)
            else:
                Bads= losses_index[-bad:]
                selected_list = selected_list + Bads
                break

    new_trial = []
    for i in selected_list:
        new_trial.append(trial.trials[i])

    empty_trial = Trials()
    trial_merged = trials_from_docs(list(empty_trial) + new_trial)

    for i, v in enumerate(trial_merged.trials):

        need_to_change = trial_merged.trials[i]['tid']

        trial_merged.trials[i]['tid'] = i
        trial_merged.trials[i]['misc']['tid'] = i
        for key in v['misc']['idxs']:
            if v['misc']['idxs'][str(key)] == [need_to_change]:
                trial_merged.trials[i]['misc']['idxs'][str(key)] = [i]
    return trial_merged





def find_n_initial_random(trial, N):
    """
    This method pick random history out of big trial
    """
    losses = trial.losses()
    losses = [abs(i) for i in losses]
    losses = np.array(losses)
    random.seed(0)
    selected_points = random.sample(range(len(losses)), N)

    new_trial = []
    for i, v in enumerate(trial.trials):
        if i in selected_points:
            new_trial.append(v)


    empty_trial = Trials()
    trial_merged = trials_from_docs(list(empty_trial) + new_trial)

    for i, v in enumerate(trial_merged.trials):

        need_to_change = trial_merged.trials[i]['tid']

        trial_merged.trials[i]['tid'] = i
        trial_merged.trials[i]['misc']['tid'] = i
        for key in v['misc']['idxs']:
            if v['misc']['idxs'][str(key)] == [need_to_change]:
                trial_merged.trials[i]['misc']['idxs'][str(key)] = [i]
    return trial_merged


# trial_bigsearchspace_5000 = pickle.load(open("/home/dfki/Desktop/Thesis/hyperopt/results_onserver/ashkan_server/bigsearchspace/trial_bigsearchspace_5000.p","rb"))
# trial_1000_new = find_n_initial(trial_bigsearchspace_5000,1000,7,993)
# pickle.dump(trial_1000_new, open('/home/dfki/Desktop/Thesis/hyperopt/results/madeup_trials/trial_1000_new_outof5000_1.p', 'wb'))

def trial_utils(trial, start, end):
    losses = trial.losses()
    losses = [abs(i) for i in losses]
    losses = np.array(losses)
    fail_config_index = np.where(losses==0)[0]
    number_failconfig = len(fail_config_index)
    number_all_try = len(losses)

    best_indices = np.argwhere(losses == np.amin(losses))
    best_indices = best_indices.flatten().tolist()

    losses = np.delete(losses,fail_config_index)
    avg_score = losses[start:end].mean()
    standard_deviation = losses[start:end].std()
    max_start_end = losses[start:end].max()

    best_score_id = trial.best_trial['tid']
    best_score = abs(trial.best_trial['result']['loss'])
    print('STD: {}'.format(standard_deviation))
    print('Best score:{} \n best score id:{} \n Average score[{},{}]:{} \n number of all try: {} \n number of fail try:{}'.format(best_score, best_score_id, start, end,
                                                                                avg_score,number_all_try,number_failconfig))
    print("Best score in [{},{}]:{}".format(start,end,max_start_end))

    print("-----------")
    return avg_score,standard_deviation,max_start_end


def time_tracker_plot(times, plot_label, xlabel, ylabel, show_plot=True):
    # print(times)
    time_keeper = []
    iteration = len(times) - 1
    for i in range(iteration):
        if times[i][0] == '0start':
            elapsedTime = times[i + 1][1] - times[i][1]
            time_keeper.append(timedelta.total_seconds(elapsedTime))


        elif (times[i][0] == 'end') or (times[i][0] == 'end_fail'):
            elapsedTime = times[i + 1][1] - times[i][1]
            time_keeper.append(timedelta.total_seconds(elapsedTime))

    time_keeper.append(timedelta.total_seconds(elapsedTime))
    print("total time point finding is {}".format(np.array(time_keeper).sum()))
    print("mean time for each configuration finding {}".format(np.array(time_keeper).mean()))
    # print(time_keeper)
    if show_plot:
        matplotlib.rcParams.update({'font.size': 20})

        fig_size = plt.rcParams["figure.figsize"]
        fig_size[0] = 15
        fig_size[1] = 5
        plt.plot(time_keeper, label='{}'.format(plot_label))
        plt.grid(True)
        plt.xlabel('{}'.format(xlabel))
        plt.ylabel('{}'.format(ylabel))
        plt.legend(loc=1)

        plt.show()


def find_n_histogram_points(trial, full_budget, n_bin, plot=False):
    budget_per_bin = int(full_budget / n_bin)

    losses = trial.losses()
    losses = [abs(i) for i in losses]
    losses = np.array(losses)
    losses_index = np.argsort(losses)
    #find index of more 0.5 accuracies
    valuable_index=[]
    valuable_points=[]
    for index,value in enumerate(losses):
        if value >= 0.5:
            valuable_index.append(index)
            valuable_points.append(value)


    print("Size of the History is {}".format(len(losses)))
    print("Size of atleast 50 accuracy is {}".format(len(valuable_index)))
    print("we need to select {} for each bin".format(budget_per_bin))
    print("Best point accuracy is {}".format(losses[losses_index[-1]]))

    selected_index = []

    def select_points(binmember):
        print(len(binmember))

        if len(binmember) == 0:
            return len(binmember)
        elif len(binmember) < budget_per_bin:
            print("change bin size")
            raise Exception
        elif len(binmember) == budget_per_bin:
            for item in binmember:
                index = np.where(losses == item)[0][0]
                selected_index.append(index)
        else:
            sampling = random.choices(binmember, k=budget_per_bin)
            for item1 in sampling:
                index1 = np.where(losses == item1)[0][0]
                selected_index.append(index1)

        print("selected number {}".format(len(selected_index)))
        return len(binmember)

    out = stats.binned_statistic(valuable_points, statistic=select_points, bins=n_bin, values=valuable_points)

    # if number of point is still not enough
    # if len(selected_index) < full_budget:
    #     diff = full_budget - len(selected_index)
    #     Bests = losses_index[-diff:]
    #     selected_index = list(selected_index) + list(Bests)
    print("Number of Selected points is {}".format(len(selected_index)))
    if plot:
        plt.hist(losses, bins=n_bin)
        plt.xlabel('Accuracy')
        plt.ylabel('N - points')
        plt.grid(True)
        plt.show()

    # build the new trial
    new_trial = []
    for i in selected_index:
        new_trial.append(trial.trials[i])

    empty_trial = Trials()
    trial_merged = trials_from_docs(list(empty_trial) + new_trial)

    for i, v in enumerate(trial_merged.trials):

        need_to_change = trial_merged.trials[i]['tid']

        trial_merged.trials[i]['tid'] = i
        trial_merged.trials[i]['misc']['tid'] = i
        for key in v['misc']['idxs']:
            if v['misc']['idxs'][str(key)] == [need_to_change]:
                trial_merged.trials[i]['misc']['idxs'][str(key)] = [i]

    return trial_merged


def find_n_special_points(trial, N, strategy):
    losses = trial.losses()
    losses = [abs(i) for i in losses]
    losses = np.array(losses)
    losses_index = np.argsort(losses)
    if strategy == 'BEST':
        selected_points = losses_index[-N:]
    elif strategy == 'WORST':
        selected_points = losses_index[:N]
    else:
        print("the strategy is not in list [Best,WORST]")


    new_trial = []
    for i, v in enumerate(trial.trials):
        if i in selected_points:
            new_trial.append(v)

    empty_trial = Trials()
    trial_merged = trials_from_docs(list(empty_trial) + new_trial)

    for i, v in enumerate(trial_merged.trials):

        need_to_change = trial_merged.trials[i]['tid']

        trial_merged.trials[i]['tid'] = i
        trial_merged.trials[i]['misc']['tid'] = i
        for key in v['misc']['idxs']:
            if v['misc']['idxs'][str(key)] == [need_to_change]:
                trial_merged.trials[i]['misc']['idxs'][str(key)] = [i]
    return trial_merged


def remove_zero_trial(trial):
    losses = trial.losses()
    losses = [abs(i) for i in losses]
    losses = np.array(losses)
    fail_config_index = np.where(losses <= 0.5)[0] # 0.47778473091364204
    number_failconfig = len(fail_config_index)
    print('Number of fail_point is {}'.format(number_failconfig))


    new_trial = []
    for i, v in enumerate(trial.trials):
        if i not in fail_config_index:
            new_trial.append(v)

    empty_trial = Trials()
    trial_merged = trials_from_docs(list(empty_trial) + new_trial)

    for i, v in enumerate(trial_merged.trials):

        need_to_change = trial_merged.trials[i]['tid']

        trial_merged.trials[i]['tid'] = i
        trial_merged.trials[i]['misc']['tid'] = i
        for key in v['misc']['idxs']:
            if v['misc']['idxs'][str(key)] == [need_to_change]:
                trial_merged.trials[i]['misc']['idxs'][str(key)] = [i]
    return trial_merged


def vector_builder(trial):


    features = trial.trials[0]['misc']['vals'].keys()
    d={}
    # d['acc'] = []
    for ii in features:
        d[ii] =[]


    for index, each_trial in enumerate(trial.trials):
        # d['acc'].append(abs(each_trial['result']['loss']))
        for i, x in enumerate(each_trial['misc']['vals']):

            if len(each_trial['misc']['vals'][x]) == 0:
                d[x].append(0.0)
                # d[x].append(np.nan)
            else:
                if str(each_trial['misc']['vals'][x][0]) in ['None',np.nan]:
                    # d[x].append(np.nan)
                    d[x].append(0.0)
                else:
                    d[x].append(float(each_trial['misc']['vals'][x][0]))

    df = pd.DataFrame.from_dict(d)
    #fill the None value with the mean of the column

    # df = df.fillna(df.mean())
    # df1 = df.dropna(axis='columns', how='all')

    vector = df.values
    print('shape vector is {}'.format(vector.shape))
    return vector



def specialindex_trial_builder(trial,selected_index):
    # build the new trial
    new_trial = []
    for i in selected_index:
        new_trial.append(trial.trials[i])

    empty_trial = Trials()
    trial_merged = trials_from_docs(list(empty_trial) + new_trial)

    for i, v in enumerate(trial_merged.trials):

        need_to_change = trial_merged.trials[i]['tid']

        trial_merged.trials[i]['tid'] = i
        trial_merged.trials[i]['misc']['tid'] = i
        for key in v['misc']['idxs']:
            if v['misc']['idxs'][str(key)] == [need_to_change]:
                trial_merged.trials[i]['misc']['idxs'][str(key)] = [i]

    return trial_merged


def selecet_index_base_kmeans(X, k, min_member):
    '''
    X: np.array
    k: number of k in kmeans
    min_member: number of sample should take out of each cluster
    '''
    kmeans = KMeans(n_clusters=k).fit(X)

    cluster_map = pd.DataFrame()
    cluster_map['data_index'] = range(0, X.shape[0])
    cluster_map['cluster'] = kmeans.labels_
    centers = np.array(kmeans.cluster_centers_)

    selected_index = []
    for i in range(k):
        l = cluster_map[cluster_map.cluster == i].index
        if len(l) <= min_member:
            selected_index = list(l) + list(selected_index)
        else:
            ceneter_i = centers[i]
            dis_list = []
            for index in l:
                dis = euclidean_distances([ceneter_i], [X[index]])
                dis_list.append(dis[0][0])
            dis_list = np.array(dis_list)
            k_closest_to_center = np.argpartition(dis_list, min_member)[:min_member]

            selected_index = list(selected_index) + list(k_closest_to_center)
        l = []

    return selected_index


def histogram_equal_percentage_base(trial, percentage, n_bin, plot=True):
    losses = trial.losses()
    losses = [abs(i) for i in losses]
    losses = np.array(losses)
    losses_index = np.argsort(losses)

    selected_index = []
    print('Percentage is {}'.format(percentage))

    def select_points(binmember):
        if len(binmember) == 0:
            return len(binmember)


        binmember = np.array(binmember)
        required_number = int((percentage / 100) * len(binmember))

        if required_number >= len(binmember):
            for i,xx in enumerate(binmember):
                selected_index.append(i)
            return len(binmember)


        list_diff = []
        for i, x in enumerate(binmember):
            list_diff.append(abs(binmember[i] - binmember.mean()))

        list_diff = np.array(list_diff)
        indexes = np.argpartition(list_diff, required_number)[:required_number]

        print("{} selected from this bin".format(len(indexes)))
        for xx in indexes:
            selected_index.append(xx)
        return len(binmember)

    out = stats.binned_statistic(losses, statistic=select_points, bins=n_bin, values=losses)

    print("Number of Selected points is {}".format(len(selected_index)))
    print("------------------------------------------------------")
    if plot:
        plt.hist(losses, bins=n_bin)
        plt.xlabel('Accuracy')
        plt.ylabel('N - points')
        plt.grid(True)
        plt.show()

    # build the new trial
    new_trial = []
    for i in list(selected_index):
        new_trial.append(trial.trials[i])

    empty_trial = Trials()
    trial_merged = trials_from_docs(list(empty_trial) + new_trial)

    for i, v in enumerate(trial_merged.trials):

        need_to_change = trial_merged.trials[i]['tid']

        trial_merged.trials[i]['tid'] = i
        trial_merged.trials[i]['misc']['tid'] = i
        for key in v['misc']['idxs']:
            if v['misc']['idxs'][str(key)] == [need_to_change]:
                trial_merged.trials[i]['misc']['idxs'][str(key)] = [i]

    return trial_merged


def histogram_equal_percentage_base_f1(trial, percentage, n_bin, plot=True):
    losses = []
    for t in trial.trials:
        losses.append(t['result']['f_measure'])

    losses = np.array(losses)
    losses_index = np.argsort(losses)

    selected_index = []

    def select_points(binmember):
        if len(binmember) == 0:
            return len(binmember)

        binmember = np.array(binmember)
        required_number = int((percentage / 100) * len(binmember))

        if required_number >= len(binmember):
            for i,xx in enumerate(binmember):
                selected_index.append(i)
            return len(binmember)

        list_diff = []
        for i, x in enumerate(binmember):
            list_diff.append(abs(binmember[i] - binmember.mean()))

        list_diff = np.array(list_diff)
        indexes = np.argpartition(list_diff, required_number)[:required_number]
        print("{} selected from this bin".format(len(indexes)))

        for xx in indexes:
            selected_index.append(xx)
        return len(binmember)

    out = stats.binned_statistic(losses, statistic=select_points, bins=n_bin, values=losses)

    print("Number of Selected points is {}".format(len(selected_index)))
    if plot:
        plt.hist(losses, bins=n_bin)
        plt.xlabel('Accuracy')
        plt.ylabel('N - points')
        plt.grid(True)
        plt.show()

    # build the new trial
    new_trial = []
    for i in selected_index:
        new_trial.append(trial.trials[i])

    empty_trial = Trials()
    trial_merged = trials_from_docs(list(empty_trial) + new_trial)

    for i, v in enumerate(trial_merged.trials):

        need_to_change = trial_merged.trials[i]['tid']

        trial_merged.trials[i]['tid'] = i
        trial_merged.trials[i]['misc']['tid'] = i
        for key in v['misc']['idxs']:
            if v['misc']['idxs'][str(key)] == [need_to_change]:
                trial_merged.trials[i]['misc']['idxs'][str(key)] = [i]

    return trial_merged


def point_base_area_under_roc_curve_classifier(trial,percentage):
    df2 = pickle.load(open("/home/dfki/Desktop/Thesis/hyperopt/result_openml/mylaptop/31/automatic/new/cluster/df2.p", "rb"))
    selected_index = []
    for i in range(14):
        l = df2[(df2["accuracy"]< 0.99) &( df2["DFC"]==i)].sort_values(by ='accuracy')['index'].to_list()
        if i==12:
            selected_index = selected_index + l
        if i == 13:
            selected_index = selected_index + l
        if len(l) < 10:
            selected_index = selected_index + l
        # else:
        #     budget = int(len(l) * (percentage/100))
        #     # sampling = random.choices(l, k=budget)
        #     # selected_index = list(selected_index) + list(sampling)
        #     step_size = int(len(l)/budget)
        #
        #     for j in range(budget):
        #         if j==0:
        #             candidate_index = l[j]
        #         else:
        #             candidate_index = l[j*step_size]
        #         selected_index.append(candidate_index)
    #make trial
    trials_made = specialindex_trial_builder(trial,selected_index)
    return trials_made

def unique_acc_selector(df,trial):
    """
    For each dataset only return the index of pipeline that has unique accuracy
    for same accuracies return the index which has more None in the row (means more easy pipelines)
    :param df: Dataframe of the dataset
    :param trial: trial of dataset
    :return: new trial with unique accuracy
    """
    selected = []
    for acc in set(df['accuracy']):
        l = np.where(df['accuracy'] == acc)
        candidate = df.iloc[l].isnull().sum(axis=1).idxmax()
        selected.append(candidate)
    print(len(selected))
    trials_made = specialindex_trial_builder(trial,selected)
    return trials_made


def Kmeans_trial_builder(X1, k, trial, method, min_member):
    ":return: new trial based on method and kmeans"

    def calculate_SSE_for_each_cluster(X, centers, cluster_map, k):
        biggest = []
        for j in range(k):
            sum_dist = []
            l = np.where([cluster_map['cluster_{}'.format(k)] == j])[1]
            for i in l:
                dist = ((X[i] - centers[k][j]) ** 2).sum()
                sum_dist.append(dist)
            print('sse for cluster {}: {}'.format(j, np.array(sum_dist).sum()))
            biggest.append(np.array(sum_dist).sum())
        sse = np.array(sum_dist).sum()

        print("k={}, sse={}".format(k, sse))
        print('Biggest sse is for cluster {}'.format(np.array(biggest).argmax()))
        print('---------------------------------------------------------')
        return (np.array(biggest).argmax())

    sse = []
    centers = {}

    cluster_map1 = pd.DataFrame()
    cluster_map1['data_index'] = range(0, X1.shape[0])

    km = KMeans(n_clusters=k)
    km.fit(X1)
    sse.append(km.inertia_)
    centers[k] = km.cluster_centers_
    cluster_map1['cluster_{}'.format(k)] = km.labels_

    cluster_map1['Cluster_number'] = km.labels_
    aa = cluster_map1.groupby('Cluster_number').count()
    print(aa['cluster_{}'.format(k)])

    print("---------------------------------------")

    if method == 'biggest_cluster':
        biggest_cluster = cluster_map1.groupby('Cluster_number').count().idxmax()[0]
        l = np.where([cluster_map1['cluster_{}'.format(k)] == biggest_cluster])[1]
    elif method == 'biggest_sse':
        biggest_sse = calculate_SSE_for_each_cluster(X1, centers, cluster_map1, k)
        l = np.where([cluster_map1['cluster_{}'.format(k)] == biggest_sse])[1]

    elif method == 'all_cluster':
        l = selecet_index_base_kmeans(X1, k, min_member)

    t = specialindex_trial_builder(trial, l)

    return t















def encoder (df):
    def encoder_categorical(df1, feature):
        A = pd.get_dummies(df1[feature])
        result = pd.concat([df1, A], axis=1)
        answer = result.drop([feature], axis=1)
        answer = pd.DataFrame(answer)
        return answer

    # find categorical columns
    categorical_columns = []
    for col in df.columns:
        if df[col].dtypes not in [int, float]:
            categorical_columns.append(col)
            df[col] = df[col].astype('category')
            df = encoder_categorical(df, col)
        else:
            df[col] = df[col].fillna(df[col].mean())
            df =pd.DataFrame(df)
    return df


def find_best_k(X1, maxk):
    # find the best K
    # Run the Kmeans algorithm and get the index of data points clusters
    print(X1.shape)
    sse = []
    centers = {}
    list_k = list(range(2, maxk))
    cluster_map1 = pd.DataFrame()
    cluster_map2 = pd.DataFrame()
    cluster_map1['data_index'] = range(0, X1.shape[0])

    for k in list_k:
        km = KMeans(n_clusters=k, random_state=0)
        km.fit(X1)
        sse.append(km.inertia_)
        centers[k] = km.cluster_centers_

        cluster_map1['cluster_{}'.format(k)] = km.labels_

        cluster_map1['Cluster_number'] = km.labels_
        aa = cluster_map1.groupby('Cluster_number').count()
        print(aa['cluster_{}'.format(k)])

        print("---------------------------------------")

    # Plot sse against k
    import pylab as plb
    plb.rcParams['font.size'] = 16
    plt.figure(figsize=(6, 6))
    plt.plot(list_k, sse, '-o')
    plt.xlabel(r'Number of clusters k')
    plt.ylabel('Sum of squared distance')
    plt.grid(True)
    return sse, centers, cluster_map1


def cluter_report(df_31,cluster_map,maxk):
    for k in range(2,maxk):

        for j in range(k):
            l = np.where([cluster_map['cluster_{}'.format(k)] == j])[1]



            print("k={}, cluster={},len={} ".format( k,j,len(l)))

            print("Data preprocessing:{}, Feature preprosser:{}, Classifier:{}".format(set(df_31['data_preprocessing'][l]),set(df_31['feature_preprocessing'][l]),set(df_31['classifier'][l])))

            print('max acc in cluster {} --- Min acc in cluster {}  ---- Mean acc{}'.format(df_31['accuracy'][l].max(),df_31['accuracy'][l].min(),df_31['accuracy'][l].mean()))
            print('------------------------------------')
        print("-------------------------------------------------------")






import seaborn as sns
def ploter(x,y, plot_label, xlabel, ylabel):
    fig_size = plt.rcParams["figure.figsize"]
    fig_size[0] = 20
    fig_size[1] = 8
    plt.plot(x,y,label='{}'.format(plot_label))
    plt.xticks(x)
    plt.yticks(range(65,99))
    plt.grid(True)
    plt.xlabel('{}'.format(xlabel))
    plt.ylabel('{}'.format(ylabel))
    plt.legend(loc=3)
    plt.show()


def expriment_ploter(experiment, title):
    import pylab as plb
    plb.rcParams['font.size'] = 16
    fig_size = plt.rcParams["figure.figsize"]
    fig_size[0] = 13
    fig_size[1] = 5
    x_axis_kmeans = []
    avg_acc_3_kmeans = []
    std_3 = []
    max_found_3 = []
    history_quality = []

    for item in experiment:
        x_axis_kmeans.append(item[0])
        avg_acc_3_kmeans.append(item[1])
        std_3.append(item[2])
        max_found_3.append(item[3])
        history_quality.append(item[4])

    d3kmeasn = {
        'History-Size': x_axis_kmeans,
        'AVG-Accuracy': avg_acc_3_kmeans,
            'std':std_3,
        'Best_found': max_found_3,
        'History_quality': history_quality
    }

    pd3kmeasn = pd.DataFrame(d3kmeasn)

    sns.set(font_scale=1.4, style='whitegrid', )
    sns.set_context("talk", font_scale=1.4, rc={"lines.linewidth": 5, 'lines.markersize': 20})

    sns.lineplot(x='History-Size', y='AVG-Accuracy', style='Approaches', legend=False,markers=True, dashes=False, hue='Approaches',
                 data=pd.melt(pd3kmeasn, ['History-Size'], value_name='AVG-Accuracy', var_name='Approaches')).set_title(
        '{}'.format(title))
    # plt.legend(bbox_to_anchor=(1.03, 1), loc=2, borderaxespad=0.)


def experiment_STD(experiment):
    import pylab as plb
    plb.rcParams['font.size'] = 16
    fig_size = plt.rcParams["figure.figsize"]
    fig_size[0] = 13
    fig_size[1] = 5
    sns.set(font_scale=1.4, style='whitegrid', )
    sns.set_context("talk", font_scale=1.4, rc={"lines.linewidth": 5, 'lines.markersize': 20})

    x_axis_kmeans = []
    avg_acc_3_kmeans = []
    std_3 = []
    max_found_3 = []
    history_quality = []
    for item in experiment:
        x_axis_kmeans.append(item[0])
        avg_acc_3_kmeans.append(item[1])
        std_3.append(item[2])
        max_found_3.append(item[3])
        history_quality.append(item[4])

    d3kmeasn = {
        'History': x_axis_kmeans,
        'AVG-Accuracy': avg_acc_3_kmeans,
        'std': std_3,
        'Best_found':max_found_3,
        'History_quality':history_quality
    }

    pd3kmeasn = pd.DataFrame(d3kmeasn)

    g = sns.FacetGrid(pd3kmeasn, height=5, aspect=3,legend_out=True)
    # g.set(ylim=(0.8,1))
    ax = g.map(plt.errorbar, "History", "AVG-Accuracy", "std",'Best_found')

    ax.set(xlabel="Percentage of bins (%)", ylabel="AVG-Accuracy")

    plt.show()



#
# import pickle
# all_trials = pickle.load(open("/home/dfki/Desktop/Thesis/openml_test/pickel_files/31/final/trial_31_withrunid1.p", "rb"))
# for iteration in list(np.arange(0, 120, 20)):
#     a=histogram_equal_percentage_base(all_trials,iteration,5,False)
#
#


# X = pickle.load(open("/home/dfki/Desktop/Thesis/hyperopt/result_openml/final_result/32/X32_f=73.p", "rb"))
# all_trials = pickle.load(open("/home/dfki/Desktop/Thesis/openml_test/pickel_files/32/final/trial_32_withrunid1.p", "rb"))
#
# trial = Kmeans_trial_builder(X, 4, all_trials, method='all_cluster', min_member=15)
# print(len(trial.trials))

# trial_1035in_histogram5bin = find_n_histogram_points(trial_3, 1035, 5, plot=True)
#
# # good_trial = find_n_initial(trial=trial_3,N=4000,good=15,bad=3987)
# # a= vector_builder(trial_3)
# import vector
# a=selecet_index_base_kmeans(trial_3,5,500)
# print(a.shape)
# # #save the result
# # # pickle.dump(trial_1035in_histogram5bin, open('/home/dfki/Desktop/Thesis/hyperopt/result_openml/mylaptop/3/automatic/new/cluster/trial_1035in_histogram5bin.p', 'wb'))
