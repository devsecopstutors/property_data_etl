# utils/check_bigints.py

import numpy as np

def detect_bigint_candidates(df, threshold=2_147_483_647):
    """
    Detect columns in a DataFrame where values exceed standard INTEGER size.
    
    Args:
        df (pd.DataFrame): The DataFrame to check.
        threshold (int): Max value for PostgreSQL INTEGER (default = 2_147_483_647).
        
    Returns:
        List[str]: Column names that should be BIGINT.
    """
    bigint_columns = []
    for col in df.select_dtypes(include=[np.number]).columns:
        max_val = df[col].max(skipna=True)
        min_val = df[col].min(skipna=True)
        
        if (max_val is not None and max_val > threshold) or (min_val is not None and min_val < -threshold):
            bigint_columns.append(col)
    
    return bigint_columns
