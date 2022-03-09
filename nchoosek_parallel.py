# -*- coding: utf-8 -*-
"""
Created on Thu Aug 26 16:38:29 2021
​
@author: craig
"""

import numpy as np
import itertools
import pandas as pd
import time
import sys

def fake_data(regions,nsubj=100, tcprate=0.3, tcpshift=0.1, thickmean=0):
    ntcp=int(nsubj*tcprate)
    tcp=np.zeros(nsubj)
    tcp[0:ntcp]=1
    df=pd.DataFrame({'TCP':tcp})
    for r in regions:
        fakethick=np.random.normal(loc=thickmean,scale=0.7,size=nsubj)
        fakethick[0:ntcp] += np.random.normal(loc=tcpshift,scale=0.2,size=ntcp)
        df[r]=fakethick
    return df

def run_all_logits(origdata,regions,k=6,target='Old?'):
    # Returns the AUC for a logit regression for all n-choose-k regions
    from sklearn.metrics import roc_auc_score
    from statsmodels.tools.tools import add_constant
    import statsmodels.api as sm 
    target_y=origdata[target]
    n=len(regions)
    # k=3
    all_combos=np.array(list(itertools.combinations(regions,k)))
    aucs=np.zeros(len(all_combos))
    print("n={} k={} combos={}".format(n,k,len(all_combos)))
    t0=time.perf_counter()
    for itr,subset in enumerate(all_combos):
        predictors=add_constant(origdata[subset])
        modelfit=sm.Logit(target_y,predictors).fit(disp=False, method='ncg')
        modelpred = modelfit.predict(predictors)
        aucs[itr]=roc_auc_score(target_y, modelpred)
        #if itr%100==0 and itr:
        #    print('{}:   {:.2f} s   {:.3f} msec/itr'.format(itr,(time.perf_counter()-t0), 1000*(time.perf_counter()-t0)/itr))
        print("Iteration: "+str(itr))
    t1=time.perf_counter()    
    print('Total time {:.2f}, {:.1f} per sec'.format(t1-t0, len(all_combos)/(t1-t0)))
    return (all_combos,aucs)    

def parrun_all_logits(origdata,regions,k=6,target='Old?',njobs=2,chunksize=1000):
    # Returns the AUC for a logit regression for all n-choose-k regions
    # Here we don't just use the simple parallelization based on single combinations
    # but have it do a whole set of 1000 or so at a time.  This greatly speeds 
    # things up as the threads get to run for several seconds each before
    # needing to rejoin and this cuts the overhead tremendously and lets
    # it scale 
    from sklearn.metrics import roc_auc_score
    from statsmodels.tools.tools import add_constant
    import statsmodels.api as sm
    from joblib import Parallel, delayed, parallel_backend
    def multi_fit(target_y,origdata,combos):
        # Pass in the range of predictors to work on
        aucs=np.zeros(len(combos))
        for itr,subset in enumerate(combos):
            predictors=add_constant(origdata[subset])
            modelfit=sm.Logit(target_y,predictors).fit(disp=False, method='ncg')
            modelpred = modelfit.predict(predictors)
            aucs[itr]=roc_auc_score(target_y, modelpred)
        return aucs   
    target_y=origdata[target]
    n=len(regions)
    all_combos=np.array(list(itertools.combinations(regions,k)))
    #aucs=np.zeros(len(all_combos))
    print("n={} k={} combos={}".format(n,k,len(all_combos)))
    t0=time.perf_counter()
    starts=np.arange(0,len(all_combos),chunksize)
    stops=np.empty_like(starts)
    stops[0:-1]=starts[1:]
    stops[-1]=len(all_combos)+1
    with parallel_backend("loky", inner_max_num_threads=1):
        aucs=list(Parallel(n_jobs=njobs)(
        delayed(multi_fit)(target_y,origdata,all_combos[starts[i]:stops[i]]) for i in range(len(starts)))
        )
    t1=time.perf_counter()    
    print('Total time {:.2f}, {:.1f} per sec'.format(t1-t0, len(all_combos)/(t1-t0)))
    return (all_combos,aucs) 
