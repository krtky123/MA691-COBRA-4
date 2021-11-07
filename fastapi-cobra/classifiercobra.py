# Licensed under the MIT License - https://opensource.org/licenses/MIT

from sklearn import neighbors, tree, svm
from sklearn.linear_model import SGDClassifier, LogisticRegression
from sklearn.utils import shuffle
from sklearn.base import BaseEstimator
from sklearn.utils.validation import check_X_y, check_array, check_is_fitted
from sklearn.naive_bayes import GaussianNB
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.neural_network import MLPClassifier

import math
import numpy as np
import random
import logging
import numbers


logger = logging.getLogger('pycobra.classifiercobra')


class ClassifierCobra(BaseEstimator):
    """
    Classification algorithm as introduced by
    Mojirsheibani [1999] Combining Classifiers via Discretization,
    Journal of the American Statistical Association.
    Parameters
    ----------
    random_state: integer or a numpy.random.RandomState object.
        Set the state of the random number generator to pass on to shuffle and loading machines, to ensure
        reproducibility of your experiments, for example.
    Attributes
    ----------
    machines: A dictionary which maps machine names to the machine objects.
            The machine object must have a predict method for it to be used during aggregation.
    machine_predictions: A dictionary which maps machine name to it's predictions over X_l
            This value is used to determine which points from y_l are used to aggregate.
    """

    def __init__(self, random_state=None, machine_list='basic'):
        self.random_state = random_state
        self.machine_list = machine_list

    def fit(self, X, y, default=True, X_k=None, X_l=None, y_k=None, y_l=None):
        """
        Parameters
        ----------
        X: array-like, [n_samples, n_features]
            Training data which will be used to create ClassifierCobra.
        y: array-like [n_samples]
            Training labels for classification.
        default: bool, optional
            If set as true then sets up COBRA with default machines and splitting.
        X_k : shape = [n_samples, n_features]
            Training data which is used to train the machines loaded into COBRA.
        y_k : array-like, shape = [n_samples]
            Target values used to train the machines loaded into COBRA.
        X_l : shape = [n_samples, n_features]
            Training data which is used during the aggregation of COBRA.
        y_l : array-like, shape = [n_samples]
            Target values which are actually used in the aggregation of COBRA.
        """

        X, y = check_X_y(X, y)
        self.X_ = X
        self.y_ = y
        self.X_k_ = X_k
        self.X_l_ = X_l
        self.y_k_ = y_k
        self.y_l_ = y_l
        self.estimators_ = {}

        # try block to pass scikit-learn estimator check.
        try:
            # set-up COBRA with default machines
            if default:
                self.split_data()
                self.load_default(machine_list=self.machine_list)
                self.load_machine_predictions()
        except ValueError:
            return self

        return self

    def pred(self, X, M, info=False):
        """
        Performs the CLassififerCobra aggregation scheme, used in predict method.
        Parameters
        ----------
        X: array-like, [n_features]
        M: int, optional
            M refers to the number of machines the prediction must be close to to be considered during aggregation.
        info: boolean, optional
            If info is true the list of points selected in the aggregation is returned.
        Returns
        -------
        result: prediction
        """

        # dictionary mapping machine to points selected
        select = {}
        for machine in self.estimators_:
            # machine prediction
            label = self.estimators_[machine].predict(X)
            select[machine] = set()
            # iterating from l to n
            # replace with numpy iteration
            for count in range(0, len(self.X_l_)):
                if self.machine_predictions_[machine][count] == label:
                    select[machine].add(count)

        points = []
        # count is the indice number.
        for count in range(0, len(self.X_l_)):
            # row check is number of machines which picked up a particular point
            row_check = 0
            for machine in select:
                if count in select[machine]:
                    row_check += 1
            if row_check == M:
                points.append(count)

        # if no points are selected, return 0
        if len(points) == 0:
            if info:
                logger.info("No points were selected, prediction is 0")
                return (0, 0)
            logger.info("No points were selected, prediction is 0")
            return 0

        # aggregate
        classes = {}
        for label in np.unique(self.y_l_):
            classes[label] = 0

        for point in points:
            classes[self.y_l_[point]] += 1

        result = int(max(classes, key=classes.get))
        if info:
            return result, points
        return result

    def predict(self, X, M=None, info=False):
        """
        Performs the ClassifierCobra aggregation scheme, calls pred.
        ClassifierCobra performs a majority vote among all points which are retained by the COBRA procedure.
        Parameters
        ----------
        X: array-like, [n_features]
        M: int, optional
            M refers to the number of machines the prediction must be close to to be considered during aggregation.
        info: boolean, optional
            If info is true the list of points selected in the aggregation is returned.
        Returns
        -------
        result: prediction
        """
        X = check_array(X)

        if M is None:
            M = len(self.estimators_)
        if X.ndim == 1:
            return self.pred(X.reshape(1, -1), M=M)

        result = np.zeros(len(X))
        avg_points = 0
        index = 0
        for vector in X:
            if info:
                result[index], points = self.pred(
                    vector.reshape(1, -1), M=M, info=info)
                avg_points += len(points)
            else:
                result[index] = self.pred(vector.reshape(1, -1), M=M)
            index += 1

        if info:
            avg_points = avg_points / len(X_array)
            return result, avg_points

        return result

    def predict_proba(self, X, kernel=None, metric=None, bandwidth=1, **kwargs):
        """
        Performs the ClassifierCobra aggregation scheme and calculates probability of a point being in a particular class.
        ClassifierCobra performs a majority vote among all points which are retained by the COBRA procedure.

        NOTE: this method is to visualise boundaries.
        The current method is just the mean of the consituent machines, as the concept of that kind of predicted probability
        doesn't exist (yet) for classifier cobra.
        Parameters
        ----------
        X: array-like, [n_features]
        """

        probs = []
        for machine in self.estimators_:
            try:
                probs.append(self.estimators_[machine].predict_proba(X))
            except AttributeError:
                continue
        prob = np.mean(probs, axis=0)
        return prob

    def split_data(self, k=None, l=None, shuffle_data=True):
        """
        Split the data into different parts for training machines and for aggregation.
        Parameters
        ----------
        k : int, optional
            k is the number of points used to train the machines.
            Those are the first k points of the data provided.
        l: int, optional
            l is the number of points used to form the ClassifierCobra aggregate.
        shuffle: bool, optional
            Boolean value to decide to shuffle the data before splitting.
        Returns
        -------
        self : returns an instance of self.
        """

        if shuffle_data:
            self.X_, self.y_ = shuffle(
                self.X_, self.y_, random_state=self.random_state)

        if k is None and l is None:
            k = int(len(self.X_) / 2)
            l = int(len(self.X_))

        if k is not None and l is None:
            l = len(self.X_) - k

        if l is not None and k is None:
            k = len(self.X_) - l

        self.X_k_ = self.X_[:k]
        self.X_l_ = self.X_[k:l]
        self.y_k_ = self.y_[:k]
        self.y_l_ = self.y_[k:l]

        return self

    def load_default(self, machine_list='basic'):
        """
        Loads 4 different scikit-learn regressors by default. The advanced list adds more machines. 
        As of current release SGD algorithm is not included in the advanced list.
        Parameters
        ----------
        machine_list: optional, list of strings
            List of default machine names to be loaded.
        Returns
        -------
        self : returns an instance of self.
        """
        if machine_list == 'basic':
            machine_list = ['sgd', 'tree', 'knn', 'svm']
        if machine_list == 'advanced':
            machine_list = ['tree', 'knn', 'svm', 'logreg',
                            'naive_bayes', 'lda', 'neural_network']

        for machine in machine_list:
            try:
                if machine == 'svm':
                    self.estimators_['svm'] = svm.SVC().fit(
                        self.X_k_, self.y_k_)
                if machine == 'knn':
                    self.estimators_['knn'] = neighbors.KNeighborsClassifier().fit(
                        self.X_k_, self.y_k_)
                if machine == 'tree':
                    self.estimators_['tree'] = tree.DecisionTreeClassifier().fit(
                        self.X_k_, self.y_k_)
                if machine == 'logreg':
                    self.estimators_['logreg'] = LogisticRegression(
                        random_state=self.random_state).fit(self.X_k_, self.y_k_)
                if machine == 'naive_bayes':
                    self.estimators_['naive_bayes'] = GaussianNB().fit(
                        self.X_k_, self.y_k_)
                if machine == 'lda':
                    self.estimators_['lda'] = LinearDiscriminantAnalysis().fit(
                        self.X_k_, self.y_k_)
                if machine == 'neural_network':
                    self.estimators_['neural_network'] = MLPClassifier(
                        random_state=self.random_state).fit(self.X_k_, self.y_k_)
            except ValueError:
                continue

        return self

    def load_machine(self, machine_name, machine):
        """
        Adds a machine to be used during the aggregation strategy.
        The machine object must have been trained using X_k and y_k, and must have a 'predict()' method.
        After the machine is loaded, for it to be used during aggregation, load_machine_predictions must be run.
        Parameters
        ----------
        machine_name : string
            Name of the machine you are loading
        machine: machine/regressor object
            The regressor machine object which is mapped to the machine_name
        Returns
        -------
        self : returns an instance of self.
        """

        self.estimators_[machine_name] = machine

        return self

    def load_machine_predictions(self, predictions=None):
        """
        Stores the trained machines' predicitons on D_l in a dictionary, to be used for predictions.
        Should be run after all the machines to be used for aggregation is loaded.
        Parameters
        ----------
        predictions: dictionary, optional
            A pre-existing machine:predictions dictionary can also be loaded.
        Returns
        -------
        self : returns an instance of self.
        """
        self.machine_predictions_ = {}
        if predictions is None:
            for machine in self.estimators_:
                self.machine_predictions_[machine] = self.estimators_[
                    machine].predict(self.X_l_)

        return self

    def load_machine_proba_predictions(self, predictions=None):
        """
        Stores the trained machines' predicitons on D_l in a dictionary, to be used for predictions.
        Should be run after all the machines to be used for aggregation is loaded.
        Parameters
        ----------
        predictions: dictionary, optional
            A pre-existing machine:predictions dictionary can also be loaded.
        Returns
        -------
        self : returns an instance of self.
        """
        self.machine_proba_predictions_ = {}
        if predictions is None:
            for machine in self.estimators_:
                try:
                    self.machine_proba_predictions_[machine] = self.estimators_[
                        machine].predict_proba(self.X_l_)
                except AttributeError:
                    self.machine_proba_predictions_[machine] = self.estimators_[
                        machine].decision_function(self.X_l_)
        return self
