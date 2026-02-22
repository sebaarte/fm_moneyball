import pandas as pd
from typing import List, Tuple, Any, Optional

class Filter:
    """Represents a single filter condition"""
    def __init__(self, column: str, operator: str, value: Any):
        self.column = column
        self.operator = operator
        self.value = value
    
    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply this filter to a DataFrame"""
        if self.operator == "==":
            return df[df[self.column] == self.value]
        elif self.operator == "!=":
            return df[df[self.column] != self.value]
        elif self.operator == ">":
            return df[df[self.column] > self.value]
        elif self.operator == "<":
            return df[df[self.column] < self.value]
        elif self.operator == ">=":
            return df[df[self.column] >= self.value]
        elif self.operator == "<=":
            return df[df[self.column] <= self.value]
        elif self.operator == "contains":
            return df[df[self.column].astype(str).str.contains(str(self.value), case=False, na=False)]
        elif self.operator == "not contains":
            return df[~df[self.column].astype(str).str.contains(str(self.value), case=False, na=False)]
        else:
            return df
    
    def __repr__(self):
        return f"Filter({self.column} {self.operator} {self.value})"

class DataManager:
    """Manages data loading, filtering, and access"""
    def __init__(self):
        self.original_df: Optional[pd.DataFrame] = None
        self.filtered_df: Optional[pd.DataFrame] = None
        self.filters: List[Filter] = []
    
    def load_data(self, df: pd.DataFrame):
        """Load data from a DataFrame"""
        self.original_df = df.copy()
        self.filtered_df = df.copy()
        self.filters = []
    
    def add_filter(self, column: str, operator: str, value: Any) -> bool:
        """Add a filter and apply all filters"""
        if self.original_df is None:
            return False
        
        if column not in self.original_df.columns:
            return False
        
        self.filters.append(Filter(column, operator, value))
        self._apply_all_filters()
        return True
    
    def remove_filter(self, index: int) -> bool:
        """Remove a filter by index"""
        if 0 <= index < len(self.filters):
            self.filters.pop(index)
            self._apply_all_filters()
            return True
        return False
    
    def update_filter(self, index: int, column: str, operator: str, value: Any) -> bool:
        """Update an existing filter"""
        if 0 <= index < len(self.filters):
            self.filters[index] = Filter(column, operator, value)
            self._apply_all_filters()
            return True
        return False
    
    def _apply_all_filters(self):
        """Apply all active filters to the original data"""
        if self.original_df is None:
            return
        
        self.filtered_df = self.original_df.copy()
        for f in self.filters:
            self.filtered_df = f.apply(self.filtered_df)
    
    def get_filtered_data(self) -> pd.DataFrame:
        """Get the current filtered DataFrame"""
        return self.filtered_df if self.filtered_df is not None else pd.DataFrame()
    
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
    
    def get_filters(self) -> List[Filter]:
        """Get current filters"""
        return self.filters