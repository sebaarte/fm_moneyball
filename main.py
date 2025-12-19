from backend.parser import *
from backend.transform import *

html_path = r'input_files/Money_test.html'


if __name__ == "__main__":
    df = parse_html(html_path).infer_objects()
    
    print(fix_numerics(df))