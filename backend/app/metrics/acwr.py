"""Acute:chronic workload ratio (ACWR) from daily training load."""

import pandas as pd 

ACUTE_WORKLOAD = 7
CHRONIC_WORKLOAD = 28
MIN_WORKLOAD = 28 

def daily_load(activity_loads: pd.Series, end: pd.Timestamp | None = None) -> pd.Series: 
  """Sum activitiy loads per calender day. Days without training get 0."""
  
  if activity_loads.empty: 
    return pd.Series(dtype=float)
  
  days = activity_loads.index.normalize()
  per_day = activity_loads.groupby(days).sum()

  if end is None:
    last_day = per_day.index.max() 
  else: 
    last_day = pd.Timestamp(end).normalize()
  
  first_day = per_day.index.min()
  all_days = pd.date_range(first_day, last_day, freq="D")

  daily = per_day.reindex(all_days, fill_value=0.0)
  return daily.astype(float)


def acwr_rolling(daily: pd.Series) -> pd.DataFrame:
  """
  ACWR with simple rolling averages(7-day acute, 28-day chronic)
  `daily` is the output of daily load: ine row per day, rest days as 0.
  """ 

  acute = daily.rolling(ACUTE_WORKLOAD, min_periods=1).mean()
  chronic = daily.rolling(CHRONIC_WORKLOAD, min_periods=1).mean()

  return pd.DataFrame({
    "acute": acute,
    "chronic": chronic, 
    "acwr": acute / chronic
  })
