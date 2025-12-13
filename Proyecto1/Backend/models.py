from typing import Optional  # Agrega esta importación para type hints
import pandas as pd
class DataStore:
    df_raw: Optional[pd.DataFrame] = None
    df_cleaned: Optional[pd.DataFrame] = None