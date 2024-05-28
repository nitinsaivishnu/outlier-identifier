import numpy as np
from scipy import stats



def get_random_30_points(df):
    """
    Extracts 30 consecutive data points starting from a random timestamp
    that is not from the last 29 data points.
    """
    max_start_index = len(df) - 30
    start_index = np.random.randint(0, max_start_index)
    return df.iloc[start_index:start_index + 30]

def detect_outliers_zscore(data, threshold=1):
    """
    Detects outliers in the data using Z-score method.
    """
    z_scores = np.abs(stats.zscore(data))
    outliers = np.where(z_scores > threshold)
    return outliers[0]