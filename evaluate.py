from statistics import mean
import numpy as np
import pandas as pd
from sklearn.metrics import r2_score, mean_squared_error, explained_variance_score
from sklearn.linear_model import LinearRegression
import wrangle
import matplotlib.pyplot as plt
import seaborn as sns


def plot_residuals(y, yhat):
    residuals = yhat - y
    plt.figure(figsize=(12,8))
    sns.scatterplot(y, residuals)
    plt.show()

def regression_errors(y, yhat):
    MSE = mean_squared_error(y, yhat)
    SSE = MSE * len(y)
    RMSE = mean_squared_error(y, yhat, squared=False)
    ESS = sum((yhat - y.mean())**2)
    TSS = ESS + SSE
    R2 = ESS/TSS

    return SSE, ESS, TSS, MSE, RMSE, R2

def baseline_mean_errors(y):
    baseline = pd.Series(y.mean(), index=np.arange(len(y)))
    MSE = mean_squared_error(y, baseline)
    SSE = MSE * len(y)
    RMSE = mean_squared_error(y,baseline, squared=False)

    return MSE, SSE, RMSE

def better_than_baseline(y, yhat):
    SSE, ESS, TSS, MSE, RMSE, R2 = regression_errors(y, yhat)

    MSE_baseline, SSE_baseline, RMSE_baseline = baseline_mean_errors(y)

    SSE_baseline = MSE_baseline * len(y)

    if SSE < SSE_baseline:
        return True
        
    else:
        return False