import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd

app = dash.Dash(__name__)

test = pd.read_csv('s3://tridata/Santa-Cruz-Sprint.csv')
females = test[test['Gender']=='F']

print(test)
print(females)

fig = px.scatter(females, x=females['Age'], y=females['Gender Place'])

app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),

    html.Div(children='''
        Dash: A web application framework for your data.
    '''),

    dcc.Graph(
        id='example-graph',
        figure=fig
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)

