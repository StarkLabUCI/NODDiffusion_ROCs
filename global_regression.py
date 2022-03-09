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
from sklearn.linear_model import LinearRegression as linreg
import statsmodels.api as sm

def get_residue_global(roi_data, roi, global_data, metric, plot=False, plot_title='PLOT REGRESSED', save=False, save_name='TEST'):
    # Regresses out global changes in metric and returns data frame with residue added.
    x = global_data["WM "+metric]
    y = roi_data[roi+" "+metric]
    model = linreg(fit_intercept=True)
    model.fit(x[:, np.newaxis], y)
    xfit = np.linspace(x.min(), x.max(), x.shape[0])
    yfit = model.predict(xfit[:, np.newaxis])
    #Get stats:
    x_met = global_data["WM "+metric]
    y_met = roi_data[roi+" "+metric]
    x_met2 = sm.add_constant(x_met)
    est = sm.OLS(y_met, x_met2)
    est2 = est.fit()
    r2 = est2.rsquared
    p = est2.pvalues[0]
    
    y_exp = model.predict(x[:, np.newaxis])
    residue = y - y_exp
    #roi_data_regressed = roi_data.assign(regressed=residue)
    reg_data = pd.DataFrame()
    reg_metric = 'Regressed ' + roi+' '+metric
    reg_data[reg_metric] = residue
    #roi_data_regressed.rename(index=str, columns={'regressed': reg_metric}, inplace=True)

    if plot == 1:
        fig, ax = plt.subplots(figsize=(10, 25))
        plt.scatter(x * 1000, y * 1000, color='b', marker="8")
        plt.plot(xfit * 1000, yfit * 1000, color='k', linewidth=2)
        ax.set_title(plot_title,
                     fontweight='bold')
        ax.set_ylabel(roi + ' ' + metric, fontweight='bold')
        ax.set_xlabel('Global tissue specific ' + metric, fontweight='bold')
        slope = model.coef_[0]
        intercept = model.intercept_
        # plt.text(9, 24, "Slope: " + slope)
        # plt.text(9, 25, "Intercept: " + intercept)

        if save == 1:
            save_prefix = output_directory + save_name
            fig.savefig(save_prefix+'.eps')

    return reg_data, p


def get_residue_multimetric_global(roi_data, roi, global_data, x_metric, y_metrics, plot=False, save=False, save_name='regressed_trial'):
    # Plots x_metric with globally regressed y_metric
    reg_data = pd.DataFrame()
    reg_data["Subjects"] = roi_data["Subjects"]
    for y_metric in y_metrics:
        roi_data_regressed, p = get_residue_global(roi_data, roi, global_data, y_metric, plot=plot, save=save)
        print(roi+' '+ y_metric+": "+str(p))
        if p<1.0:
            reg_metric = 'Regressed ' + roi+' '+ y_metric
            reg_data[reg_metric] = roi_data_regressed[reg_metric]
        else:
            reg_metric = 'Non-Regressed ' + roi+' '+ y_metric
            reg_data[reg_metric] = roi_data[roi+' '+ y_metric]
            

        if plot == 1:
            scatter_xy(roi_data_regressed,
                       [y_metric, reg_metric],
                       x_metric + ' vs. ' + y_metric + ' in the ' + roi,
                       x=x_metric, save=save, save_name=save_name)

    return reg_data
