# -*- coding: utf-8 -*-
"""

@author: hamsi
"""

import numpy as np
import sys
import os
import math
import pandas as pd
import scipy.stats
import seaborn as sns
from matplotlib import pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression as linreg
from sklearn.linear_model import LogisticRegression as logreg
import statsmodels.api as sm


def log_reg(origdata, metric_name, method, nperms=100, shuffle=False, plot=True, target='Old?'):    
    # Get AUC of predicting <target> using just <metric_name>
    target_y=origdata[target]
    predictors=origdata[regions]
    
    predictors = add_constant(predictors)
    modelfit=sm.Logit(target_y,predictors).fit(disp=False, method='ncg') #to prevent non_hessian matrix error
    
    modelpred = modelfit.predict(predictors)
    auc=roc_auc_score(target_y, modelpred)
#     print('AUC = {:.3f}'.format(auc))
    if plot: #get ROC curves
        FPR,TPR,thresholds=roc_curve(target_y, modelpred)
        plt.figure()
        plt.plot(FPR,TPR,[0,1],[0,1],color="black")
        plt.xlim([0,1])
        plt.xlabel("False positive rate (1-specificity)")
        plt.ylabel("True positive rate (Sensitivity)")
        plt.ylim([0,1])
        axs=plt.gca()
        axs.set_aspect('equal')
        plt.title(metric_name)
    prob=np.nan
    if shuffle: #generate null distribution to get p values.
        iterations=np.zeros(nperms) # Will save AUC
        for i in range(nperms):
            shuffle_y=np.random.permutation(target_y)
            shufflefit=sm.Logit(shuffle_y,predictors).fit(disp=False, method='ncg') #to prevent non_hessian matrix error
            shufflepred = shufflefit.predict(predictors)
            shuffleauc=roc_auc_score(shuffle_y, shufflepred)
            #print(shuffleauc)
            iterations[i]=shuffleauc
        falsepos_count = np.count_nonzero(iterations>auc)
        prob =  falsepos_count / nperms
        print('prob shuffle w AUC >= {:.3f}: {:.3f}'.format(auc,prob))
        if plot:
            sns.displot(iterations,bins=20,kde=True, color="k")
            plt.axvline(auc, color="purple")
            plt.xlabel("Area under curve (AUC)")
            plt.ylabel("Number of draws")
            plt.title(metric_name)
    return auc,prob

def fake_data(target='Old?', nsubj=100, tcprate=0.3, tcpshift=0.1, thickmean=0, regions=["Left PRC", "Right PRC", "Left ERC", "Right ERC", "Left PHC", "Right PHC", "Left DG-CA3", "Right DG-CA3", "Left CA1", "Right CA1", "Left Subiculum", "Right Subiculum"]):
    ntcp=int(nsubj*tcprate)
    tcp=np.zeros(nsubj)
    tcp[0:ntcp]=1
    df=pd.DataFrame({target:tcp})
    for r in regions:
        fakethick=np.random.normal(loc=thickmean,scale=0.7,size=nsubj)
        fakethick[0:ntcp] += np.random.normal(loc=tcpshift,scale=0.2,size=ntcp)
        df[r]=fakethick
    return df

def test_logit(target='Old?'):
    shifts=[0.5, 0.2, 0.0]
    rates=[0.3, 0.5]
    for shift in shifts:
        for rate in rates:
            fdf=fake_data(tcpshift=shift,tcprate=rate)
            print('\n\n')
            print('--------------------------------------------------------')
            print('Shift= {} Rate= {}  TCP={}  nonTCP={}'.format(shift,rate,np.sum(fdf[target]==1), np.sum(fdf[target]==0)))
            print(fdf.groupby('Old?').mean())
            iterations, mean_accuracy=log_reg(fdf)
            print('  NoShuffle:  Acc={:.3f}  AUC={:.3f}'.format(mean_accuracy[0],mean_accuracy[1]))
            iterations, mean_accuracy=log_reg(fdf,shuffle=True)
            print('  Shuffle:  Acc={:.3f}  AUC={:.3f}'.format(mean_accuracy[0],mean_accuracy[1]))
