import pandas as pd



def parse_html(file_path) -> pd.DataFrame:
    table = pd.read_html(file_path)

    return table[0]

