from hyperopt import fmin, tpe, hp, STATUS_OK,Trials
from sklearn.preprocessing import Normalizer,scale,StandardScaler,MinMaxScaler
import openml
from sklearn.pipeline import Pipeline
from sklearn.decomposition import PCA
from sklearn.decomposition import FastICA
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import cross_val_score
import numpy as np
from sklearn.metrics import accuracy_score
from hyperopt import space_eval
import copy
from sklearn.decomposition import KernelPCA
from sklearn import linear_model
import pickle
import time
from sklearn import metrics
from sklearn.metrics import roc_auc_score
import datetime
from datetime import timedelta
import temp
from sklearn.compose import ColumnTransformer, make_column_transformer
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.feature_selection import VarianceThreshold
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.naive_bayes import BernoulliNB
from sklearn_extra.kernel_methods import EigenProClassifier as FKCEigenPro
from sklearn.svm import SVC
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.neural_network import MLPClassifier


class run_hyperopt(object):
    def __init__(self,dataset_id,task_id):
        self.task_id = task_id
        self.dataset_id = dataset_id

        self.task = openml.tasks.get_task(self.task_id)
        self.dataset = openml.datasets.get_dataset(dataset_id)
        self.X, self.y, self.categorical_indicator, attribute_names = self.dataset.get_data(
            dataset_format='array',
            target=self.dataset.default_target_attribute
        )
        self.copy_X = copy.deepcopy(self.X)
        self.copy_y = copy.deepcopy(self.y)
        self.time_tracker=[]

    def rest_x_y(self):
        self.X = self.copy_X
        self.y = self.copy_y

    def make_search_space(self):
        search_space={
            'data_preprocessing':hp.choice('data_preprocessing',[
                {'type':'Normalizer'},
                {'type':'SimpleImputer'},
                {'type':'ColumnTransformer',
                 'remainder':hp.choice('ColumnTransformer__remainder',["drop", "passthrough"])},
                {'type':'standard_scaler'},
                {'type':'minmaxscaler'},
                {'type':"do_noting"}
            ]),

            'feature_preprocessing':hp.choice('feature_preprocessing',[
                    {'type':'pca',
                    'iterated_power': hp.choice('pca__iterated_power', range(1,10)),
                    'n_components': hp.choice('pca__n_components',range(1,self.X.shape[1])),
                    'svd_solver':hp.choice('pca__svd_solver',['auto','full','randomized']),
                    'tol': hp.uniform('pca__tol',0,0.5),
                    'whiten': hp.choice('pca__whiten', [True, False])},

                    {'type':'kernel_pca',
                     # 'kernel':hp.choice('kernel',["linear","poly","rbf","sigmoid","cosine"]),
                     'n_components':hp.choice('n_components',range(10,self.X.shape[1]))
                     },

                    {   'type':'VarianceThreshold',
                        'threshold':hp.uniform('threshold',0,0.5)
                    },

                    {'type':'do_noting'}

            ]),

            'classifier':hp.choice('classifier',[
                {'type':'rf',
                'criterion': hp.choice('randomforestclassifier__criterion', ["gini", "entropy"]),
                'max_depth': hp.choice('randomforestclassifier__max_depth', range(2,1000)),
                'min_samples_leaf': hp.choice('randomforestclassifier__min_samples_leaf', range(1,20)),
                'min_samples_split': hp.choice('randomforestclassifier__min_samples_split', range(2,20)),
                'min_weight_fraction_leaf': hp.uniform('randomforestclassifier__min_weight_fraction_leaf', 0.0, 0.5),
                'max_features': hp.choice('randomforestclassifier__max_features', ['auto', 'sqrt', 'log2']),
                'n_estimators': hp.choice('randomforestclassifier__n_estimators', range(10,1000)),
                'oob_score': hp.choice('randomforestclassifier__oob_score', [True, False]),
                 },

                {'type':'tree',
                 'criterion': hp.choice('decisiontreeclassifier__criterion', ["gini", "entropy"]),
                 'max_depth':hp.choice('decisiontreeclassifier__max_depth',[0.0009035528566034845,None]),
                 'min_samples_leaf': hp.choice('decisiontreeclassifier__min_samples_leaf', range(1, 9)),
                 'min_samples_split': hp.choice('decisiontreeclassifier__min_samples_split', [9,10]),
                 },

                {'type':'GBC',
                 'criterion': hp.choice('gradientboostingclassifier__criterion', ["friedman_mse", "mse"]),
                 'learning_rate':hp.uniform('gradientboostingclassifier__learning_rate',0.00010056450840281946, 9.920058705184867e-05),
                 'max_depth': hp.choice('gradientboostingclassifier__max_depth', range(1,9)),
                 'max_features':hp.uniform('gradientboostingclassifier__max_features', 0.00015525642662705952, 0.9998642646284683),
                 'min_impurity_decrease':hp.uniform('gradientboostingclassifier__min_impurity_decrease',0.00022898940251292466, 0.9996576747926129),
                 'min_samples_leaf':hp.choice('gradientboostingclassifier__min_samples_leaf',range(1,9)),
                 'min_samples_split':hp.choice('gradientboostingclassifier__min_samples_split',[9,10]),
                 'min_weight_fraction_leaf':hp.uniform('gradientboostingclassifier__min_weight_fraction_leaf',0.0001884133057376003, 8.873194131375772e-05),
                'n_estimators':hp.choice('gradientboostingclassifier__n_estimators',range(100,995)),
                 'n_iter_no_change':hp.choice('gradientboostingclassifier__n_iter_no_change',range(1,999)),
                 'subsample':hp.uniform('gradientboostingclassifier__subsample',0.0002081432615039791, 9.236456951389194e-06),
                 'tol':hp.uniform('gradientboostingclassifier__tol',0.0001001692053800057, 9.996741607059855e-05),
                 'validation_fraction':hp.uniform('gradientboostingclassifier__validation_fraction',0.00027270272088730785, 0.99676753787075),
                },

                {'type':'BNB',
                 'fit_prior':hp.choice('bernoullinb__fit_prior',[True,False]),
                 'alpha':hp.uniform('bernoullinb__alpha', 0.010073368015954882, 98.93346969207758),

                },
                {'type':'fkceigenpro',
                'degree':hp.choice('fkceigenpro__degree',range(2,4)),
                 'gamma':hp.uniform('fkceigenpro__gamma', 0.0001, 1e-10),
                 'kernel':hp.choice('fkceigenpro__kernel',["laplace", "rbf"]),
                 'n_components':hp.choice("fkceigenpro__n_components",range(500,1000))

                },

                {'type':'svc',
                 'C':hp.uniform("svc__C", 0.01,9979.44679282882),
                 'coef0':hp.uniform('svc__coef0',-0.0001901088806708362, 0.9996939328918386),
                 'degree':hp.choice('svc__degree',range(1,5)),
                 'gamma':hp.uniform('svc__gamma', 0.00010001864000043732, 9.984514749387293e-05),
                 'kernel':hp.choice('svc__kernel',["linear", "sigmoid"]),
                 'shrinking':hp.choice('svc__shrinking',[True,False]),
                 'tol':hp.uniform('svc__tol', 0.00010032523263523512, 9.990234352037583e-05),
                },

                {'type':'KN',
                 'n_neighbors':hp.choice('KN_n_neighbors',range(2,10)),
                 'algorithm':hp.choice('KN_algorithm',['auto', 'ball_tree', 'kd_tree', 'brute'])
                 },

                {'type':'etree',
                 'bootstrap':hp.choice('extratreesclassifier__bootstrap',[True,False]),
                 'criterion': hp.choice('extratreesclassifier__criterion', ["gini", "entropy"]),
                 'max_features': hp.uniform('extratreesclassifier__max_features',
                                            0.00296553169445235, 0.9884684507203433),
                 'min_samples_leaf': hp.choice('extratreesclassifier__min_samples_leaf', range(1, 9)),
                 'min_samples_split': hp.choice('extratreesclassifier__min_samples_split', [9, 10]),
                },
                {'type':'MLP',
                 'activation':hp.choice('mlpclassifier__activation',["identity", "tanh"]),
                 'alpha':hp.uniform('mlpclassifier__alpha',0.00010695575243507994, 6.541497552990362e-05),
                 'batch_size':hp.choice('mlpclassifier__batch_size',['auto',95]),
                 'beta_1':hp.uniform('mlpclassifier__beta_1', 0.00544424784765507, 0.9),
                 'beta_2': hp.uniform('mlpclassifier__beta_2', 0.047423225221743026, 0.999),
                'early_stopping':hp.choice('mlpclassifier__early_stopping',[True,False]),
                 'hidden_layer_sizes':hp.choice('mlpclassifier__hidden_layer_sizes',range(951,1013)),
                 'learning_rate':hp.choice('mlpclassifier__learning_rate',["adaptive", "invscaling"]),
                 'learning_rate_init':hp.uniform('mlpclassifier__learning_rate_init',0.00013450694347599834,7.740530907783659e-05),
                 'max_iter':hp.choice('mlpclassifier__max_iter',range(992,1003)),
                 'momentum':hp.uniform('mlpclassifier__momentum',0.06610188576749942, 0.983051121954481),
                 'n_iter_no_change':hp.choice('mlpclassifier__n_iter_no_change',range(10,987)),
                 'nesterovs_momentum':hp.choice('mlpclassifier__nesterovs_momentum',[True,False]),
                 'power_t':hp.uniform('mlpclassifier__power_t',0.0002094262206310496, 5.7659652445073064e-05),
                 'shuffle':hp.choice('mlpclassifier__shuffle',[True,False]),
                 'solver':hp.choice('mlpclassifier__solver',["adam", "sgd"]),
                 'tol':hp.uniform('mlpclassifier__tol',0.0001, 7.072577204620778e-05),
                },

                {'type':'SGD',
                 'loss':hp.choice('loss',["log", "modified_huber", "squared_hinge", "perceptron"]),
                 'penalty':hp.choice('penalty',["l1", "l2", "elasticnet"]),
                 'alpha':hp.uniform('alpha',1e-7,1e-1),
                 'max_iter':hp.choice('max_iter',range(5,1000)),
                 'tol':hp.uniform('tol',1e-5, 1e-1)}
            ])

        }
        return search_space

    def objective(self,params):
        try:
            print("--------------------")
            start = datetime.datetime.now()
            self.time_tracker.append(start)

            print(params)
            copy_params = copy.deepcopy(params)
            step=[]
            data_preprocessing_type = params['data_preprocessing']['type']
            del params['data_preprocessing']['type']

            if data_preprocessing_type == 'Normalizer':
                scaler = Normalizer()
                self.X = scaler.fit_transform(self.X)


            elif data_preprocessing_type == 'SimpleImputer':
                scaler = SimpleImputer(missing_values=np.nan, strategy='mean')
                self.X = scaler.fit_transform(self.X)


            elif data_preprocessing_type == 'ColumnTransformer':
                scaler = make_column_transformer((OneHotEncoder(), [i for i in range(self.X.shape[1])]),remainder=params['data_preprocessing']['remainder'])
                self.X = scaler.fit_transform(self.X)


            elif data_preprocessing_type == 'standard_scaler':
                scaler = StandardScaler()
                self.X = scaler.fit_transform(self.X)


            elif data_preprocessing_type == 'minmaxscaler':
                scaler = MinMaxScaler()
                self.X = scaler.fit_transform(self.X)


            elif data_preprocessing_type == 'do_noting':
                pass


            feature_preprocessing_type = params['feature_preprocessing']['type']
            del params['feature_preprocessing']['type']

            if feature_preprocessing_type == 'pca':
                pca_params = params['feature_preprocessing']
                pca  = PCA()
                pca.set_params(**pca_params)
                pca.random_state = 0
                step.append(('pca',pca))

            elif feature_preprocessing_type =='VarianceThreshold':
                variance_params = params['feature_preprocessing']
                variance = VarianceThreshold()
                variance.set_params(**variance_params)
                self.X = variance.fit_transform(self.X)


            elif feature_preprocessing_type == 'kernel_pca':
                kernel_pca_param = params['feature_preprocessing']
                kernel_pca = KernelPCA()
                kernel_pca.set_params(**kernel_pca_param)
                kernel_pca.random_state = 0
                step.append(('kernel_pca',kernel_pca))

            elif feature_preprocessing_type == 'do_noting':
                pass

            classifier_type = params['classifier']['type']
            del params['classifier']['type']

            if classifier_type == 'rf':
                rf_params = params['classifier']
                rf = RandomForestClassifier()
                rf.set_params(**rf_params)
                rf.random_state  = 0
                step.append(('randomforestclassifier',rf))

            elif classifier_type =='tree':
                tree_params = params['classifier']
                tree = DecisionTreeClassifier(max_features=1.0,min_impurity_decrease=0.0,min_weight_fraction_leaf=0.0,random_state=1001,splitter='best')
                tree.set_params(**tree_params)
                step.append(('decisiontreeclassifier',tree))

            elif classifier_type =='GBC':
                gbc_params = params['classifier']
                gbc  = GradientBoostingClassifier(random_state=0)
                gbc.set_params(**gbc_params)
                step.append(('gradientboostingclassifier',gbc))

            elif classifier_type =='BNB':
                bnb_params = params['classifier']
                bnb = BernoulliNB()
                bnb.set_params(**bnb_params)
                step.append(('bernoullinb',bnb))

            elif classifier_type =='fkceigenpro':
                fkce_params = params['classifier']
                fkce = FKCEigenPro(random_state=10045)
                fkce.set_params(**fkce_params)
                step.append(('fkceigenpro',fkce))

            elif classifier_type =='svc':
                svc_params = params['classifier']
                svc = SVC(cache_size=200,random_state=1)
                svc.set_params(**svc_params)
                step.append(('svc',svc))

            elif classifier_type == 'KN':
                kn_params = params['classifier']
                kn = KNeighborsClassifier()
                kn.set_params(**kn_params)
                kn.random_state = 0
                step.append(('KN',kn))

            elif classifier_type == 'etree':
                etree_params = params['classifier']
                etree = ExtraTreesClassifier(random_state=10211,n_estimators=100)
                etree.set_params(**etree_params)
                step.append(('extratreesclassifier',etree))

            elif classifier_type == 'MLP':
                mlp_params = params['classifier']
                mlp = MLPClassifier(random_state=10431)
                mlp.set_params(**mlp_params)
                step.append(('mlpclassifier',mlp))

            elif classifier_type == 'SGD':
                sgd_params = params['classifier']
                sgd = linear_model.SGDClassifier()
                sgd.set_params(**sgd_params)
                sgd.random_state = 0
                step.append(('SGD', sgd))


            pip = Pipeline(steps=step)


            aucs=[]
            accuracies =[]
            for i in range(10):
                train_indices, test_indices = self.task.get_train_test_split_indices(fold=i)
                X_train = self.X[train_indices]
                y_train = self.y[train_indices]
                X_test = self.X[test_indices]
                y_test = self.y[test_indices]

                pip.fit(X_train, y_train)
                predicted = pip.predict(X_test)

                # predict_proba = pip.predict_proba(X_test)
                # scores = np.amax(predict_proba, axis=1)

                # auc = roc_auc_score(y_test,scores)
                # aucs.append(auc)
                fold_accuracy = accuracy_score(y_test, predicted)
                accuracies.append(fold_accuracy)

            # full_auc = np.array(aucs).mean()
            accuracy = np.array(accuracies).mean()

            # if 'do_noting' in (copy_params['data_preprocessing']['type']):
            #     pass
            # else:
            self.rest_x_y()


            print(" \n Accuracy is {}".format(accuracy))
            # print("AUC is {}".format(full_auc))
            return {'loss': -accuracy, 'status': STATUS_OK}
        except:
            print("The config has problem")
            return {'loss': 0, 'status': STATUS_OK}





if __name__ == '__main__':

    runner = run_hyperopt(31,31)
    trials = Trials()

    best,trials_inside = fmin(runner.objective, runner.make_search_space(), algo=tpe.suggest, max_evals=10, trials=trials,rstate=np.random.RandomState(10))
    print("Best Accuracy is {}\n {} \n".format(trials_inside.best_trial['result']['loss'],best))
    print(space_eval(runner.make_search_space(),best))

    temp.trial_utils(trials_inside,0,100)
    temp.time_tracker_plot(runner.time_tracker, 'time', 'iteration', 'time(sec)}', show_plot=False)
