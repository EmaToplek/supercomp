"""Acute:chronic workload ratio (ACWR) from daily training load."""

import pandas as pd 
import numpy as np

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

def _acwr_table(acute: pd.Series, chronic: pd.Series) -> pd.DataFrame: 
  """
  Combine acute and chronic load into a table with acwr and status. 
  For the first 27 days acwr is NaN and status is "insufficient_data".
  """

  day_number = np.arange(1, len(acute) + 1)
  enough_data = day_number >= MIN_WORKLOAD

  acwr = acute / chronic.replace(0, np.nan)
  acwr = acwr.where(enough_data)

  return pd.DataFrame({
    "acute": acute,
    "chronic": chronic, 
    "acwr": acwr,
    "status": np.where(enough_data, "ok", "insufficient_data")
  })



def acwr_rolling(daily: pd.Series) -> pd.DataFrame:
  """
  ACWR with simple rolling averages(7-day acute, 28-day chronic)
  `daily` is the output of daily load: ine row per day, rest days as 0.
  """ 

  acute = daily.rolling(ACUTE_WORKLOAD, min_periods=1).mean()
  chronic = daily.rolling(CHRONIC_WORKLOAD, min_periods=1).mean()

  return _acwr_table(acute, chronic)

def acwr_ewma(daily: pd.Series) -> pd.DataFrame: 
  """
  ACWR with exponentially weighted averages.
  Recent days count more and old day fade out slowl, so acwr does not jump when a hard day leaves the
  window like it does with rolling averages.
  """
  ewma_acute = daily.ewm( span=ACUTE_WORKLOAD, adjust=False).mean()
  ewma_chronic = daily.ewm(span=CHRONIC_WORKLOAD,adjust=False).mean()
  return _acwr_table(ewma_acute, ewma_chronic)
  
