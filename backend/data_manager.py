import pandas as pd
from typing import List, Tuple, Any, Optional, Dict


categories = ["General","Goals","Assists","Goal Contributions","Shots","Passes","Dribbles","Crossing", "Chances Created","Pressing","Possession","Penalties","Tackles","Interceptions","Blocks"
              ,"Headers","Fouls","Clearances","Offsides","Distance","Saves","Conceded","Cards","Misc","Computed"]

general = ["Name","Position","Age","Club","Division","Nationality","Home-Grown Status","Personality","Media handling","Wage","Transfer Value","Asking Price",
           "Preferred Foot","Starts","Sub Appearances","Minutes Played","Minutes/game","Average Rating"]
goals = ["Goals","Goals/90","Minutes/Goal","xG","xG/90","xG/Shot","xG Overperformance","xG Overperformance/90","Non-Penalty Goals","Non-Penalty Goals/90",
         "Non-pen Goals/Shot","Minutes/Non-pen Goal","Non-pen xG","Non-pen xG/90","Non-Penalty Goals - Non-pen xG/90","Non-Penalty xD/Shot","Non-Pen xG Overperformance"
         ,"Non-Pen xG Overperformance/90","Conversion %","Goals Inside Box","Goals Inside Box/90","Goals Inside Box %","Inside Box Conversion %"
         ,"Goals Outside Box","Goals Outside Box/90","Goals Outside Box %","Outside Box Conversion %"]
assists = ["Assists","Assists/90","Minutes/Assist","xA","xA/90","xA Overperformance","xA Overperformance/90","Assists/Clear Cut Chances Created"]

goal_contributions = ["Goal Contributions","Goal Contributions/90","xGC","xGC/90","xGC Overperformance","xGC Overperformance/90","Non-penalty GC",
                      "Non-penalty GC/90","Non-penalty xGC","Non-penalty xGC/90","Non-penalty xGC Overperformance","Non-penalty xGC Overperformance/90"]

shots = ["Shots","Shots/90","Shots on target","Shots on target/90","Shot Accuracy %","Shots Inside Box","Shots Inside Box/90","Shots Inside Box %",
        "Shots Outside Box","Shots Outside Box/90","Shots Outside Box %"]

passes = ["Passes Attempted","Passes Attempted/90","Passes Completed","Passes Completed/90","Pass Completion %","Progressive Passes","Progressive Passes/90","Progressive Pass Rate",
          "Key Passes","Key Passes/90","Key Pass %","Open Play Key Passes","Open Play Key Passes/90","Open Play Key Pass %"]

crossing = ["Crosses Attempted","Crosses Attempted/90","Crosses Completed","Crosses Completed/90","Cross Completion %",
            "Open Play Crosses Attempted","Open Play Crosses Attempted/90","Open Play Crosses Completed","Open Play Crosses Completed/90","Open Play Cross Completion %"]

chances_created = ["Chances Created","Chances Created/90","Clear Cut Chances Created","Clear Cut Chances Created/90","Clear Cut Chances %"]

pressing = ["Pressures Attempted","Pressures Attempted/90","Pressures Completed","Pressures Completed/90","Press Completion %"]

possession = ["Possession Won","Possession Won/90","Possession Lost","Possession Lost/90","Possession differential / 90"]

dribbles = ["Dribbles / 90","Dribbles Completed"]

penalties = ["Penalties Taken","Penalties Scored","Penalty Conversion %"]

tackles = ["Tackles Attempted","Tackles Attempted/90","Tackles Completed","Tackles Completed/90","Tackle Completion %", "Tackles Failed","Tackles Failed/90","Key Tackles"
           ,"Key Tackles/90","Key Tackle %", "Tackle Quality"]

interceptions = ["Intereceptions","Interceptions/90"]

blocks = ["Blocks","Blocks/90","Shots Blocked","Shots Blocked/90"]

headers = ["Headers Attempted","Headers Attempted/90","Headers Won","Headers Won/90","Header Won %","Headers Lost","Headers Lost/90","Header Lost %","Key Headers","Key Headers/90","Key Header %",
           "Aerial Duels Attempted","Aerial Duels Attempted/90","Aerial Duels Won","Aerial Duels Win %"]

fouls = ["Fouls Against","Fouls Made","Net Fouls","Fouls Won / 90","Fouls Committed / 90"]

clearances = ["Clearances","Clearances/90"]

offsides = ["Offsides","Offsides/90","Offsides per Non-Penalty Goal"]

distance = ["Distance Covered","Distance Covered/90"]

saves = ["Total Saves","Saves/90","Save %","xSave","xSave %","xSave % Overperformance","Saves Held","Saves Held/90","Saves Held %","Saves Held/Shots Faced",
         "Saves Tipped","Saves Tipped/90","Saves Tipped %","Saves Tipped / Shots Faced","Saves Parried","Saves Parried/90","Saves Parried %","Saves Parried / Shots Faced",
         "Saves/Goal Conceded", "Save Efficiency","Shots on target Against","Shots on target Against/90","xGP (expected Goals prevented)","xGP/90","Penalites Faced","Penalties Saved","Penalty Save %"]

conceded = ["Goals Conceded","Goals Conceded/90","Clean Sheets","Clean Sheet Ratio"]

cards = ["Yellow Cards","Yellow Cards/90","Red Cards","Red Cards/90","Yellows/Tackle","Reds/Tackle"]

misc = ["Player Of the match Awards","Mistakes Leading to Goal","Sprints","Sprints/90"]




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
    MASTER_TAB_ID = "Master Data"
    
    def __init__(self):
        self.original_df: Optional[pd.DataFrame] = None
        self.percentile_df: Optional[pd.DataFrame] = None
        self.data_source_path: Optional[str] = None
        # Per-tab filter collections: {tab_id: [Filter, ...]}
        self.tab_filters: Dict[str, List[Filter]] = {}
    
    def load_data(self, df: pd.DataFrame, source_path: Optional[str] = None):
        """Load data from a DataFrame"""
        self.original_df = df.copy()
        self.data_source_path = source_path
        self.tab_filters = {}
        self._compute_percentiles()
    
    def _compute_percentiles(self):
        """Compute percentiles for all numeric columns"""
        if self.original_df is None:
            self.percentile_df = None
            return
        
        percentile_data = {}
        for column in self.original_df.columns:
            if pd.api.types.is_numeric_dtype(self.original_df[column]):
                # Compute percentile rank (0-100)
                percentile_data[f"{column}_percentile"] = self.original_df[column].rank(pct=True) * 100
        
        if percentile_data:
            self.percentile_df = pd.DataFrame(percentile_data, index=self.original_df.index)
        else:
            self.percentile_df = None
    
    def add_filter(self, tab_id: str, column: str, operator: str, value: Any) -> bool:
        """Add a filter for a specific tab"""
        if self.original_df is None:
            return False
        
        # Check both original columns and percentile columns
        all_cols = self.get_columns()
        if column not in all_cols:
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
        """Get filtered data for a specific tab (with percentiles and global filters)"""
        if self.original_df is None:
            return pd.DataFrame()
        
        # Start with original data + percentiles
        if self.percentile_df is not None:
            filtered = pd.concat([self.original_df.copy(), self.percentile_df], axis=1)
        else:
            filtered = self.original_df.copy()
        
        # Apply global filters from Master Data tab first
        if self.MASTER_TAB_ID in self.tab_filters:
            for f in self.tab_filters[self.MASTER_TAB_ID]:
                filtered = f.apply(filtered)
        
        # Apply tab-specific filters
        if tab_id is not None and tab_id != self.MASTER_TAB_ID and tab_id in self.tab_filters:
            for f in self.tab_filters[tab_id]:
                filtered = f.apply(filtered)
        
        return filtered
    
    def get_columns(self) -> List[str]:
        """Get list of available columns (including percentiles)"""
        if self.original_df is None:
            return []
        
        columns = list(self.original_df.columns)
        if self.percentile_df is not None:
            columns.extend(list(self.percentile_df.columns))
        
        return columns
    
    def get_column_dtype(self, column: str) -> str:
        """Get the data type of a column"""
        if self.original_df is None:
            return "object"
        
        if column in self.original_df.columns:
            return str(self.original_df[column].dtype)
        elif self.percentile_df is not None and column in self.percentile_df.columns:
            return str(self.percentile_df[column].dtype)
        
        return "object"
    
    def get_unique_values(self, column: str) -> List[Any]:
        """Get unique values for a column (useful for filters)"""
        if self.original_df is None:
            return []
        
        if column in self.original_df.columns:
            return self.original_df[column].dropna().unique().tolist()[:100]
        elif self.percentile_df is not None and column in self.percentile_df.columns:
            return self.percentile_df[column].dropna().unique().tolist()[:100]
        
        return []
    
    def get_filters(self, tab_id: str) -> List[Filter]:
        """Get filters for a specific tab"""
        return self.tab_filters.get(tab_id, [])
    
    def clear_tab_filters(self, tab_id: str):
        """Clear all filters for a specific tab"""
        if tab_id in self.tab_filters:
            self.tab_filters[tab_id] = []
