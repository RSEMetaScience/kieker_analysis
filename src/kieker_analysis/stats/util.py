import numpy as np
import pandas as pd

def min_max_normalise(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    out = df.copy()

    col_min = out[columns].min()
    col_max = out[columns].max()
    denom = (col_max - col_min).replace(0, np.nan)   # avoid divide-by-zero

    out[columns] = (out[columns] - col_min) / denom
    out[columns] = out[columns].fillna(0.0)          # constant columns -> 0.0

    return out