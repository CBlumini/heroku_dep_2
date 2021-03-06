import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
pd.set_option("precision", 2)
import dash
from dash import dcc
from dash import html
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table
import os
import time

data = pd.read_csv('https://github.com/CBlumini/heroku_dep_2/raw/main/Santa-Cruz-Sprint.csv', header=0, index_col=None)

#the data does not come in the right form to do math on it. So convert the times to minutes and decimal seconds
#maybe setup a compute file to do this by itself later
def create_time_columns(bare_frame):
    def convertTime (time):
        temp = time.split(':')
        timeMinutes = (int(temp[0])*60)+int(temp[1])+int(temp[2])/60
        return timeMinutes

    #convert to integers
    bare_frame["Swim Minutes"] = bare_frame["Swim"].apply(convertTime)
    bare_frame["T1 Minutes"] = bare_frame["T1"].apply(convertTime)
    bare_frame["Bike Minutes"] = bare_frame["Bike"].apply(convertTime)
    bare_frame["T2 Minutes"] = bare_frame["T2"].apply(convertTime)
    bare_frame["Run Minutes"] = bare_frame["Run"].apply(convertTime)
    #bare_frame["Elapsed Minutes"] = bare_frame["Chip Elapsed"].apply(convertTime)

    #create cumulative times
    bare_frame["Swim+T1"]=round(bare_frame["Swim Minutes"]+bare_frame["T1 Minutes"], 2)
    bare_frame["Plus Bike"]=round(bare_frame["Swim+T1"]+bare_frame["Bike Minutes"], 2)
    bare_frame["Plus T2"]=round(bare_frame["Plus Bike"]+bare_frame["T2 Minutes"], 2)
    bare_frame["Total"]=round(bare_frame["Plus T2"]+bare_frame["Run Minutes"], 2)

    return bare_frame


time_df = create_time_columns(data)

reduced2 = time_df[["Name","Swim Minutes","Swim+T1","Plus Bike","Plus T2","Total","Gender Place"]]
reduced2["Start"] = 0

#create the para coord plot
dimensions = list([
            dict(range = [0, 1],
                label = 'Start', values = reduced2['Start']),            
            dict(range = [reduced2["Swim Minutes"].min(), reduced2["Swim Minutes"].max()],
                label = 'Time After Swim', values = reduced2['Swim Minutes']),
            dict(range = [reduced2["Swim+T1"].min(), reduced2["Swim+T1"].max()],
                label = 'Time After First Transition', values = reduced2['Swim+T1']),
            dict(range = [reduced2["Plus Bike"].min(), reduced2["Plus Bike"].max()],
                label = 'Time After Bike', values = reduced2['Plus Bike']),
            dict(range = [reduced2["Plus T2"].min(), reduced2["Plus T2"].max()],
                label = 'Time After Second Transition', values = reduced2['Plus T2']),
            dict(range = [reduced2["Total"].min(), reduced2["Total"].max()],
                label = 'Total Time', values = reduced2['Total']),
            dict(range=[0,reduced2['Gender Place'].max()], tickvals = reduced2['Gender Place'], ticktext = reduced2['Name'],
                    label='Competitor', values=reduced2['Gender Place'])
        ])

para_cor = go.Figure(data=go.Parcoords(line = dict(color = reduced2['Gender Place'],
                colorscale = [[.0,'rgba(255,0,0,0.1)'],[0.2,'rgba(0,255,0,0.1)'],[.4,'rgba(0,0,255,0.1)'], 
                                [.6,'rgba(0,255,255,0.1)'], [.8, 'rgba(255,0,255,0.1)'], [1, 'rgba(0,0,0,0.1)']]), dimensions=dimensions))

para_cor.update_layout(
    title="Triathalon Results",
    width=1920,
    height=1080)

#create a scatter plot
scatter = px.scatter(time_df, x=time_df['Age'], y=time_df['Div Place'], trendline = 'ols')
#scatter.show()


#create the dash app
app = dash.Dash(__name__, external_stylesheets = [dbc.themes.BOOTSTRAP])
server = app.server
app.config.suppress_callback_exceptions = True

#set the app.layout so we have two tabs
app.layout = html.Div([
    dcc.Tabs(id="tabs", value='tab-1', children=[dcc.Tab(label='Data Table', value='tab-1'), 
                                                 dcc.Tab(label='Age vs Performance', value='tab-2'),
                                                 dcc.Tab(label='Performance Plot', value='tab-3'),]),
    html.Div(id='tabs-content')
])

#create a data table, name the columns
dash_columns=["Bib", "Name", "Age", "Gender", "Team Name", "City", "Swim", "T1", "Bike", "T2", "Run", "Chip Elapsed", "Div Place", "Age Place", 
              "Gender Place"]
#create the page
@app.callback(Output('tabs-content', 'children'), [Input('tabs', 'value')])
def render_content(tab):
    if tab == 'tab-1':
        return html.Div(dash_table.DataTable(
                            id='table-sorting-filtering',
                            columns=[{'name': i, 'id': i} for i in dash_columns],
                            data=time_df.to_dict('records'),
                            style_table={'overflowX': 'scroll'},
                            style_cell={
                                'height': '90',
                                #'minWidth': '110%',
                                'minWidth': '60px', 'width': '100px', 'maxWidth': '140px',
                                'whiteSpace': 'normal', 'textAlign': 'center'},
                            style_cell_conditional=[        {
                                'if': {'column_id': 'Name'},
                                'textAlign': 'center'
                                    }],
                            page_current= 0,
                            page_size=15,
                            filter_action='native',
                            filter_query='',
                            sort_action='native',
                            sort_mode='single',
                            sort_by=[],
                            style_as_list_view=True,
                            hidden_columns=[],
                        )
                        )
    elif tab == 'tab-2':
        return dcc.Graph(figure=scatter)
    
    elif tab == 'tab-3':
        return dcc.Graph(figure=para_cor)

app.run_server(debug=True, use_reloader=False) 



