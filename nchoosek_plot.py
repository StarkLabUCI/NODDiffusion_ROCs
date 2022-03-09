# -*- coding: utf-8 -*-
"""

@author: hamsi
"""

import os
import pandas as pd
import statsmodels.api as sm
import pandas as pd 
from sklearn import datasets, linear_model
from sklearn.model_selection import train_test_split
from matplotlib import pyplot as plt
import numpy as np
import seaborn as sns
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
import pandas as pd      
from sklearn.metrics import (confusion_matrix, accuracy_score)
from sklearn.metrics import roc_auc_score
from sklearn.metrics import roc_curve
from statsmodels.tools.tools import add_constant
import sys
from roc_analysis import log_reg

def get_data_frame(rawdata,democog_file):
    sga = pd.read_csv(democog_file) #file with cognitive and demographic data
    df = pd.merge(sga, rawdata, on="Subject") 
    return df

def plot_hist_with_AUCs(combos_filename,aucs_filename,rawfile,metriccol_dict,target,age_mode='all',plot=True,bins=20):
    df_combos = pd.read_csv(combos_filename+".csv").iloc[1: , 1:]
    df_aucs = pd.read_csv(aucs_filename+".csv").iloc[1: , 1:]
    aucs = pd.DataFrame(np.array(df_aucs).flatten('F'))
    df_combos['AUCs'] = aucs
    if plot:
        fig, ax = plt.subplots()
        sns.displot(np.array(aucs), fill=True, bins=bins, legend = False)
        perc = np.percentile(np.array(df_aucs.dropna()).flatten('C'),99)
        for m in metriccol_dict:
            color = metriccol_dict[m]
            raw = pd.read_csv(rawfile)
            dfn = get_data_frame(raw)
            if age_mode == "old":
                dfn = dfn[dfn["Old?"]==1]
            if age_mode == "yng":
                dfn = dfn[dfn["Old?"]==0]
            oauc = log_reg(dfn, m, 'ncg', target=target)
            plt.axvline(oauc, label=m, linewidth=2, linestyle="-", color=color)
        print(perc)
        plt.xlabel("Area under curve (AUC)")
        plt.ylabel("Number of draws")
        locs, labels = plt.yticks()
        plt.xlim(0.5,1.0)
        plt.annotate('99th', xy=(perc, 0), xytext=(perc+0.005, 0.5*locs[1]), arrowprops = dict(arrowstyle = 'simple')) #arrowprops = dict(facecolor='black', shrink=0.2, width = 0.5, headwidth = 0.5, headlength = 0.5))
        # plt.savefig(aucs_filename+".png", bbox_inches = 'tight')

    return df_combos

def get_besties(combos_filename, df_combos, method='AUC', top_rows=500, top_AUC=0.85, splitx=2, metriccol_dict = {'NDI':'darkblue','ODI':'dodgerblue','w_csf.w':'aquamarine','fa':'maroon', 'adx10':'mediumvioletred','adcx10':'coral','rdx10':'gold','volume':'dimgrey'}):
    df_combos = df_combos.sort_values(by=['AUCs'],ascending=False)
    regshp_dict = {'DG-CA3':'o', 'CA1':'^', 'Subiculum':','}
    
    if method == 'AUC':
        top_AUC = np.percentile(np.array(df_combos["AUCs"].dropna()).flatten('C'),99)
        df_thresh = df_combos[df_combos["AUCs"] > top_AUC]
    else:
        df_thresh = df_combos.head(top_rows)
    
    allROIs = pd.DataFrame(np.array(df_thresh.drop(['AUCs'],axis=1)).flatten('C'))
    distribution = allROIs.groupby([0]).size()
    distribution.index.name = 'ROIs'
    distribution.name = 'Predicted'
    orderedROIs = distribution.sort_values().index
#     orderedROIs = distribution.index
    distribution = distribution.reindex(orderedROIs, axis=1)
    
    fig, ax = plt.subplots()
    plt.figure()
#     labels = [item.get_text() for item in ax.get_xticklabels()]
    labels = list(str(',') * len(orderedROIs))
    for i in range(len(orderedROIs)):
        ll = orderedROIs[i]
        met = ll.split(' ')[splitx]
        reg = ll.split(' ')[1]
        shape = regshp_dict[reg]
        color = metriccol_dict[met]
        labels[i] = str(ll[0])+' '+str(ll.split(' ')[1])
        plt.scatter(orderedROIs[i],distribution[i], color=color, marker=shape)
    ax.set_xticklabels(labels)
    plt.xticks(rotation=45, ha='right', fontsize=6)
    plt.xlabel('Predictors',fontsize=12)
    plt.ylabel('Frequency of selection for top AUC',fontsize=12)
    # plt.savefig(combos_filename+"_perc-99.png", bbox_inches = 'tight')
#     plt.title(title,fontsize=16)
    return orderedROIs

def kdeplot(target,age_mode='all',plot=True,bins=20):
    tens_fn = target+"_tensors_novol_"+age_mode+"_aucs"
    nod_fn = target+"_NODDI_novol_"+age_mode+"_aucs"
    all_fn = target+"_all_metrics_novol_"+age_mode+"_aucs"
    tens_pd = pd.read_csv(tens_fn+".csv").iloc[1: , 1:]
    nod_pd = pd.read_csv(nod_fn+".csv").iloc[1: , 1:]
    all_pd = pd.read_csv(all_fn+".csv").iloc[1: , 1:]
    tens_arr = np.array(tens_pd).flatten('F')
    nod_arr = np.array(nod_pd).flatten('F')
    all_arr = np.array(all_pd).flatten('F')
    sns.set_style("white")
    fig, ax = plt.subplots()
    sns.kdeplot(tens_arr, ax=ax, color='tomato', fill=True, alpha=.5, linewidth=4, label='Tensor Metrics only')
    sns.kdeplot(nod_arr, ax=ax, color='steelblue', fill=True, alpha=.5, linewidth=4, label='NODDI Metrics only')
    sns.kdeplot(all_arr, ax=ax, color='rebeccapurple', fill=True, alpha=.5, linewidth=4, label='Both tensor and NODDI metrics')
    ax.legend(bbox_to_anchor=(0.05, 1.02), loc='upper left')
    plt.xlabel("Area under curve (AUC)")
    plt.ylabel("Distribution [%]")
    plt.xlim(0.5,1.0)
    sns.despine()
    # plt.show()
    # fig.savefig(target+"_"+age_mode+"kdeplot.png", bbox_inches = 'tight')

def get_99th_perc(aucs_filename):
    df_aucs = pd.read_csv(aucs_filename+".csv").iloc[1: , 1:].dropna()
    perc = np.percentile(np.array(df_aucs).flatten('C'),99)
    print(aucs_filename+" 99th percentile = "+str(perc))
    return perc

def what_perc_is_this(auc, filename,metric):
    df_aucs = pd.read_csv(filename+".csv").iloc[1: , 1:].dropna()
    df_aucs = np.array(df_aucs).flatten('C')
    perc = stats.percentileofscore(df_aucs, auc, kind='strict')
    print(metric+": "+str(perc))
    return perc
