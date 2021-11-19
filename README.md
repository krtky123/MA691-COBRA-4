![MA691-COBRA-4](https://user-images.githubusercontent.com/45942031/140724100-ba8da381-431a-47fa-9026-ff82cafb9719.png)

## 🐍 What is COBRA?

COBRA stands for COmBined Regression Alternative. It is a new method for combining several initial estimators of the regression function. Instead of building a linear or convex optimized combination over a collection of basic estimators r1, . . . , rM, we use them as a collective indicator of the proximity between the training data and a test observation. This local distance approach is model-free and very fast. More specifically, the resulting nonparametric/nonlinear combined estimator is shown to perform asymptotically at least as well in the L2 sense as the best combination of the basic estimators in the collective.

## 🧑‍💻 Project Members

This project has been made by AB Satyraprakash, Kartikay Goel, Samiksha Sachdeva, Jatin Dhingra, Himanshu Yadav. The work has been mentored by Prof. Arabin Kumar Dey.

## 📝 Project description

This project uses 2 famous credit risk datasets namely -  **German credit analysis** dataset and **Australian credit analysis** dataset. It implements COBRA to make accurate prediction after combining different estimators. The datasets have been taken from the UCI Machine Learning Repository: <br>
* [Statlog (German Credit Data) Data Set](https://archive.ics.uci.edu/ml/datasets/statlog+(german+credit+data))
* [Statlog (Australian Credit Approval) Data Set](https://archive.ics.uci.edu/ml/datasets/statlog+(australian+credit+approval))

## 🎯 Accuracy

Using COBRA, an accuracy of 
* **70.19%** has been obtained for German dataset and
* **85.53%** has been obtained for Australian dataset

For the complete implmentations on Google Colab see these notebooks - [Australian notebook](https://colab.research.google.com/drive/1LINYdH-g7mv-n0upWWbaLt0F-og5Y8y-?usp=sharing), [German notebook](https://colab.research.google.com/drive/1J6auH5XnrtWSmduiI2x71WhT_0BoUdyq?usp=sharing)

## 🌐 Presentation

The project has been presented as a [website](https://survival-prediction-cobra4.herokuapp.com/). The backend (API with docs) has been hosted [here](https://pacific-dawn-32033.herokuapp.com/docs). The australian dataset cannot be presented as a webapp because we do not have variable or value names due to data confidentiality issues.

## 🧰 Techstack

The following techstack has been used for the project implementation and presentation.
![Untitled design](https://user-images.githubusercontent.com/45942031/140725411-e0d855f5-a0bb-40c9-8a7c-21e6f8f13e4c.png)

## ⚠️ Disclaimer

This work is for learning purpose only. The work can not be used for publication or as commercial products etc without mentor’s consent.
