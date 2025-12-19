import pandas as pd
from pandas import DataFrame
import re
from backend.models import *



def fix_positions(df) -> pd.DataFrame:
    df['Fixed_Positions'] = df['Position'].apply(parse_positions)
    return df
    
    

def parse_positions(position_string) -> list[str]:
    pos = []
    pattern = r'([A-Z]+(?:/[A-Z]+)*)\s*\(([LCR]+)\)'

    matches = re.findall(pattern, position_string)

    for position, sides_str in matches:
        # Split the sides string into individual characters
        sides = list(sides_str)
        if '/' in position:
            sub_positions = position.split('/')
            for sub_pos in sub_positions:
                for side in sides:
                    pos.append(f"{sub_pos}{side}")
        else:
            for side in sides:
                pos.append(f"{position}{side}")

    return pos


def fix_wage(df) -> DataFrame:
    f = lambda x :  re.sub(r'\D','',str(x))

    df['Wage'] = pd.to_numeric(df['Wage'].apply(f),errors='coerce')

    return df

def fix_value(df) -> TransferRange:
    def f(x):
        bounds = []
        l = str(x).split('-')
        if len(l) == 0:
            return TransferRange(-1,-1)
        if l == ["Not for Sale"]:
            return TransferRange(float('inf'),float('inf'))
        if l == ["Unknown"]:
            return TransferRange(-1,-1)
        for i in l:
            if 'K' in i:
                bounds.append(int(re.sub(r'\D','',str(i)))*1_000)
            elif 'M' in i:
                bounds.append(int(re.sub(r'\D','',str(i)))*1_000_000)
            
            else:
                bounds.append(int(re.sub(r'\D','',str(i))))
        return TransferRange(bounds[0], bounds[1]) if len(bounds) > 1 else TransferRange(bounds[0], bounds[0])
        

    df['Transfer Value'] = df['Transfer Value'].apply(f)

    return df

def fix_numerics(df) -> DataFrame:
    return df.apply(pd.to_numeric, errors='ignore')
