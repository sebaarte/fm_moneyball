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
    f = lambda x :  re.sub('\D','',str(x))

    df['Wage'] = pd.to_numeric(df['Wage'].apply(f),errors='coerce')

    return df

def fix_value(df) -> DataFrame:
    def f(x):
        l = x.split('-')
        for i in l:
            if 'K' in i:
                return int(re.sub('\D','',str(i)))*1000
        return int(re.sub('\D','',str(l[0])))

    df['Value'] = df['Value'].apply(f)

    return df