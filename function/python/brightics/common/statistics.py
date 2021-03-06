import pandas as pd
import numpy as np
import scipy.stats 

# NOTE: all parameter 'a' is assumed as array-like


def max(a): return np.max(a)


def min(a): return np.min(a)


def range(a): return np.max(a) - np.min(a)


def sum(a): return np.sum(a)


def mean(a): return np.mean(a)


def var(a): return np.var(a)


def var_samp(a): return np.var(a, ddof=1)


def std(a): return np.std(a)


def skewness(a): return scipy.stats.skew(a)


def kurtosis(a): return scipy.stats.kurtosis(a)


def median(a): return np.median(a)


def percentile(a, q): return np.percentile(a, q * 100.0)


def trimmed_mean(a, proportiontocut): return scipy.stats.trim_mean(a, proportiontocut)


def iqr(a): return scipy.stats.iqr(a)


def q1(a): return np.percentile(a, 25)


def q3(a): return np.percentile(a, 75)


def mode(a): return list(pd.Series(a).mode())


def num_row(a): return len(a)


def num_value(a): return np.count_nonzero(~pd.isnull(a))


def num_nan(a): return np.count_nonzero([x is np.nan for x in a])


def num_nullonly(a): return np.count_nonzero([x is None for x in a])


def num_null(a): return np.count_nonzero(pd.isnull(a))


def num_distinct(a): return np.count_nonzero(np.unique(a))

