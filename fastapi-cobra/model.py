# model and path libraries
from pathlib import Path
import joblib

# data analysis libraries
from sklearn.metrics import accuracy_score
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
import numpy as np
import pandas as pd

# cobra library
import classifiercobra

# visualization libraries
import matplotlib.pyplot as plt
import seaborn as sns

# ignore warnings
import warnings
warnings.filterwarnings('ignore')
# ---------------------------------------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve(strict=True).parent

titanic_train_data = BASE_DIR.joinpath('data/train.csv')
titanic_test_data = BASE_DIR.joinpath('data/test.csv')


def train():
    # cleaning of tha data before training -----------------------------------------------------------------

    # import train and test CSV files
    train = pd.read_csv(titanic_train_data)
    test = pd.read_csv(titanic_test_data)

    # drop Cabin column because it has much less data
    train = train.drop('Cabin', axis=1)
    test = test.drop('Cabin', axis=1)

    # we can also drop the Ticket feature since it's unlikely to yield any useful information
    train = train.drop(['Ticket'], axis=1)
    test = test.drop(['Ticket'], axis=1)

    # sort the ages into logical categories
    train["Age"] = train["Age"].fillna(-0.5)
    test["Age"] = test["Age"].fillna(-0.5)
    bins = [-1, 0, 5, 12, 18, 24, 35, 60, np.inf]
    labels = ['Unknown', 'Baby', 'Child', 'Teenager',
              'Student', 'Young Adult', 'Adult', 'Senior']
    train['AgeGroup'] = pd.cut(train["Age"], bins, labels=labels)
    test['AgeGroup'] = pd.cut(test["Age"], bins, labels=labels)

    # replacing the missing values in the Embarked feature with S - since it has the maximum count
    train = train.fillna({"Embarked": "S"})

    # create a combined group of both datasets
    combine = [train, test]

    # extract a title for each Name in the train and test datasets
    for dataset in combine:
        dataset['Title'] = dataset.Name.str.extract(
            ' ([A-Za-z]+)\.', expand=False)

    pd.crosstab(train['Title'], train['Sex'])

    # replace various titles with more common names
    for dataset in combine:
        dataset['Title'] = dataset['Title'].replace(['Lady', 'Capt', 'Col',
                                                    'Don', 'Dr', 'Major', 'Rev', 'Jonkheer', 'Dona'], 'Rare')

        dataset['Title'] = dataset['Title'].replace(
            ['Countess', 'Lady', 'Sir'], 'Royal')
        dataset['Title'] = dataset['Title'].replace('Mlle', 'Miss')
        dataset['Title'] = dataset['Title'].replace('Ms', 'Miss')
        dataset['Title'] = dataset['Title'].replace('Mme', 'Mrs')

    train[['Title', 'Survived']].groupby(['Title'], as_index=False).mean()

    # map each of the title groups to a numerical value
    title_mapping = {"Mr": 1, "Miss": 2, "Mrs": 3,
                     "Master": 4, "Royal": 5, "Rare": 6}
    for dataset in combine:
        dataset['Title'] = dataset['Title'].map(title_mapping)
        dataset['Title'] = dataset['Title'].fillna(0)

    # fill missing age with mode age group for each title
    mr_age = train[train["Title"] == 1]["AgeGroup"].mode()  # Young Adult
    miss_age = train[train["Title"] == 2]["AgeGroup"].mode()  # Student
    mrs_age = train[train["Title"] == 3]["AgeGroup"].mode()  # Adult
    master_age = train[train["Title"] == 4]["AgeGroup"].mode()  # Baby
    royal_age = train[train["Title"] == 5]["AgeGroup"].mode()  # Adult
    rare_age = train[train["Title"] == 6]["AgeGroup"].mode()  # Adult

    age_title_mapping = {1: "Young Adult", 2: "Student",
                         3: "Adult", 4: "Baby", 5: "Adult", 6: "Adult"}

    for x in range(len(train["AgeGroup"])):
        if train["AgeGroup"][x] == "Unknown":
            train["AgeGroup"][x] = age_title_mapping[train["Title"][x]]

    for x in range(len(test["AgeGroup"])):
        if test["AgeGroup"][x] == "Unknown":
            test["AgeGroup"][x] = age_title_mapping[test["Title"][x]]

    # map each Age value to a numerical value
    age_mapping = {'Baby': 1, 'Child': 2, 'Teenager': 3,
                   'Student': 4, 'Young Adult': 5, 'Adult': 6, 'Senior': 7}
    train['AgeGroup'] = train['AgeGroup'].map(age_mapping)
    test['AgeGroup'] = test['AgeGroup'].map(age_mapping)

    # dropping the Age feature for now, might change
    train = train.drop(['Age'], axis=1)
    test = test.drop(['Age'], axis=1)

    # drop the name feature since it contains no more useful information.
    train = train.drop(['Name'], axis=1)
    test = test.drop(['Name'], axis=1)

    # map each Sex value to a numerical value
    sex_mapping = {"male": 0, "female": 1}
    train['Sex'] = train['Sex'].map(sex_mapping)
    test['Sex'] = test['Sex'].map(sex_mapping)

    # map each Embarked value to a numerical value
    embarked_mapping = {"S": 1, "C": 2, "Q": 3}
    train['Embarked'] = train['Embarked'].map(embarked_mapping)
    test['Embarked'] = test['Embarked'].map(embarked_mapping)

    # fill in missing Fare value in test set based on mean fare for that Pclass
    for x in range(len(test["Fare"])):
        if pd.isnull(test["Fare"][x]):
            pclass = test["Pclass"][x]  # Pclass = 3
            test["Fare"][x] = round(
                train[train["Pclass"] == pclass]["Fare"].mean(), 4)

    # map Fare values into groups of numerical values
    train['FareBand'] = pd.qcut(train['Fare'], 4, labels=[1, 2, 3, 4])
    test['FareBand'] = pd.qcut(test['Fare'], 4, labels=[1, 2, 3, 4])

    # drop Fare values
    train = train.drop(['Fare'], axis=1)
    test = test.drop(['Fare'], axis=1)

    # ------------------------------------------------------------------------------------------------------

    predictors = train.drop(['Survived', 'PassengerId'], axis=1)
    target = train["Survived"]
    x_train, x_val, y_train, y_val = train_test_split(
        predictors, target, test_size=0.22, random_state=0)

    cobra = classifiercobra.ClassifierCobra()
    cobra.fit(x_train, y_train)

    joblib.dump(cobra, Path(BASE_DIR).joinpath("cobra.joblib"))


def predict(feature_vector):
    model_file = Path(BASE_DIR).joinpath("cobra.joblib")

    # the model has not been trained.
    if not model_file.exists():
        return False

    cobra = joblib.load(model_file)

    survived = int(cobra.predict(feature_vector))
    survived_proba = cobra.predict_proba(feature_vector)

    return [survived, survived_proba[0][survived]]


def convert(prediction_list):
    prediction = {
        'survived_bool': prediction_list[0], 'survived_proba': prediction_list[1]}
    return prediction
