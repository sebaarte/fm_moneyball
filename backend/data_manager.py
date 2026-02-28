import pandas as pd
from typing import List, Tuple, Any, Optional, Dict

class Filter:
    """Represents a single filter condition"""
    def __init__(self, column: str, operator: str, value: Any):
        self.column = column
        self.operator = operator
        self.value = value

    def _cast_value_to_column_type(self, df: pd.DataFrame) -> Any:
        """Cast self.value to match the column's dtype"""
    
        if self.column not in df.columns:
            return self.value
        
        col_dtype = df[self.column].dtype
        
        try:
            # Integer types
            if pd.api.types.is_integer_dtype(col_dtype):
                return int(float(self.value))
            
            # Float types
            elif pd.api.types.is_float_dtype(col_dtype):
                return float(self.value)
            
            # Boolean types
            elif pd.api.types.is_bool_dtype(col_dtype):
                if isinstance(self.value, str):
                    return self.value.lower() in ('true', '1', 'yes', 'on')
                return bool(self.value)
            
            # Datetime types
            elif pd.api.types.is_datetime64_any_dtype(col_dtype):
                return pd.to_datetime(self.value)
            
            # String/Object types
            else:
                return str(self.value)
                
        except (ValueError, TypeError) as e:
            print(f"Warning: Could not cast '{self.value}' to {col_dtype}: {e}")
            return self.value
        
    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply this filter to a DataFrame"""
        filter_value = self._cast_value_to_column_type(df)
        
        if self.operator == "==":
            return df[df[self.column] == filter_value]
        elif self.operator == "!=":
            return df[df[self.column] != filter_value]
        elif self.operator == ">":
            return df[df[self.column] > filter_value]
        elif self.operator == "<":
            return df[df[self.column] < filter_value]
        elif self.operator == ">=":
            return df[df[self.column] >= filter_value]
        elif self.operator == "<=":
            return df[df[self.column] <= filter_value]
        elif self.operator == "contains":
            return df[df[self.column].astype(str).str.contains(str(filter_value), case=False, na=False)]
        elif self.operator == "not contains":
            return df[~df[self.column].astype(str).str.contains(str(filter_value), case=False, na=False)]
        else:
            return df
    
    def __repr__(self):
        return f"Filter({self.column} {self.operator} {self.value})"

class DataManager:
    """Manages data loading, filtering, and access"""
    def __init__(self):
        self.original_df: Optional[pd.DataFrame] = None
        self.data_source_path: Optional[str] = None
        # Per-tab filter collections: {tab_id: [Filter, ...]}
        self.tab_filters: Dict[str, List[Filter]] = {}
    
    def load_data(self, df: pd.DataFrame, source_path: Optional[str] = None):
        """Load data from a DataFrame"""
        self.original_df = df.copy()
        self.data_source_path = source_path
        self.tab_filters = {}
    
    def add_filter(self, tab_id: str, column: str, operator: str, value: Any) -> bool:
        """Add a filter for a specific tab"""
        if self.original_df is None:
            return False
        
        if column not in self.original_df.columns:
            return False
        
        if tab_id not in self.tab_filters:
            self.tab_filters[tab_id] = []
        
        self.tab_filters[tab_id].append(Filter(column, operator, value))
        return True
    
    def remove_filter(self, tab_id: str, index: int) -> bool:
        """Remove a filter by index for a specific tab"""
        if tab_id in self.tab_filters and 0 <= index < len(self.tab_filters[tab_id]):
            self.tab_filters[tab_id].pop(index)
            return True
        return False
    
    def update_filter(self, tab_id: str, index: int, column: str, operator: str, value: Any) -> bool:
        """Update an existing filter for a specific tab"""
        if tab_id in self.tab_filters and 0 <= index < len(self.tab_filters[tab_id]):
            self.tab_filters[tab_id][index] = Filter(column, operator, value)
            return True
        return False
    
    def get_filtered_data(self, tab_id: Optional[str] = None) -> pd.DataFrame:
        """Get filtered data for a specific tab"""
        if self.original_df is None:
            return pd.DataFrame()
        
        if tab_id is None or tab_id not in self.tab_filters:
            return self.original_df.copy()
        
        filtered = self.original_df.copy()
        for f in self.tab_filters[tab_id]:
            filtered = f.apply(filtered)
        
        return filtered
    
    def get_columns(self) -> List[str]:
        """Get list of available columns"""
        if self.original_df is None:
            return []
        return list(self.original_df.columns)
    
    def get_column_dtype(self, column: str) -> str:
        """Get the data type of a column"""
        if self.original_df is None or column not in self.original_df.columns:
            return "object"
        return str(self.original_df[column].dtype)
    
    def get_unique_values(self, column: str) -> List[Any]:
        """Get unique values for a column (useful for filters)"""
        if self.original_df is None or column not in self.original_df.columns:
            return []
        return self.original_df[column].dropna().unique().tolist()[:100]  # Limit to 100
    
    def get_filters(self, tab_id: str) -> List[Filter]:
        """Get filters for a specific tab"""
        return self.tab_filters.get(tab_id, [])
    
    def clear_tab_filters(self, tab_id: str):
        """Clear all filters for a specific tab"""
        if tab_id in self.tab_filters:
            self.tab_filters[tab_id] = []
