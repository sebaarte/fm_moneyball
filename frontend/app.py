import dash
from dash import dcc, html
import pandas as pd
import plotly.express as px

# Placeholder: Load data from backend (update as needed)
data_path = "./input_files/Money_test.html"
df = pd.read_html(data_path)[0]

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Moneyball Dashboard"),
    dcc.Graph(
        id="example-graph",
        figure=px.bar(df, x=df.columns[0], y=df.columns[1]) if len(df.columns) > 1 else {}
    ),
    html.Div([
        html.P("Data preview:"),
        dcc.Markdown(df.head().to_markdown())
    ])
])

if __name__ == "__main__":
    app.run(debug=True)