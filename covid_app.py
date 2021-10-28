'''
Covid Dashboard

'''
import dash
from dash import dcc,html,Input,Output,State,dash_table
import dash_bootstrap_components as dbc

import numpy as np
import pandas as pd
import plotly.express as px
import requests
import json

import os

## Start dash APP
app = dash.Dash(external_stylesheets = [ dbc.themes.BOOTSTRAP,dbc.icons.BOOTSTRAP,dbc.icons.FONT_AWESOME])

## covid data API
#url = "https://api.covid19api.com/summary"
#response_world = requests.request("GET", url)

dirName = os.path.dirname(os.path.abspath('__file__'))

fileOpen = open(os.path.join(os.path.join(dirName,'assets'),'data.json'))
data = json.load(fileOpen)

df_Global = pd.DataFrame(data['Global'],index=[0])
df_Countries = pd.DataFrame(data['Countries'])
df_last_updated = data['Date']

countryCode = open(os.path.join(os.path.join(dirName,'assets'),'country_codes.json'))
df_CountryCode = pd.DataFrame(json.load(countryCode))

df_world = pd.merge(df_Countries[['Country','TotalConfirmed','TotalDeaths','TotalRecovered','CountryCode']],
                    df_CountryCode, left_on = 'CountryCode',right_on = 'alpha-2',how = 'inner')


### covid cases
confirmed = df_Global['TotalConfirmed'][0]
newconfirmed = df_Global['NewConfirmed'][0]
deaths = df_Global['TotalDeaths'][0]
newdeaths = df_Global['NewDeaths'][0]
recovered = df_Global['TotalRecovered'][0]
newrecovered = df_Global['NewRecovered'][0]

## covid cases on world map
def worldMap(dataframe):
    fig = px.choropleth(dataframe,locations="iso_alpha",
                  color="TotalConfirmed", hover_name= "Country",
                  hover_data= ['TotalConfirmed','TotalDeaths','TotalRecovered'],
                  projection="orthographic",
                  color_continuous_scale=px.colors.sequential.Plasma
                  )
    fig.update_layout(margin = dict(l=4,r=4,t=4,b=4))
    return fig


##  Header Layout
navbar = dbc.Navbar(
    dbc.Container([
            html.Div(
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(html.Img(src=app.get_asset_url('covid_logo.png'), height="50px")),
                        
                        dbc.Col(dbc.NavbarBrand("Covid Dashboard", className="ms-2")),
                    ],
                    align="center",
                    className="g-0",
                ),
                href="https://www.who.int/health-topics/coronavirus",
                style={"textDecoration": "none"},
            ),style={'margin-left':'30px'}
            ),
            dbc.Button(id= "help_button",children="Help Us",color="dark", className="ms-2", n_clicks=0)
            
        ],fluid=True
    )
)


## Moving Info
moving_info = dbc.Row(
                html.Marquee("Covid cases are at peak. please wear mask and follow hygiene. Data last updated on "+ str(df_last_updated)),style = {'color':'green'}
                )


### Card Info function
def getCardInfo(title,totalValue,newValue,cardColor):

    cardInfo = dbc.Card([
                    dbc.CardHeader(title),
                    dbc.CardBody([
                        html.H4(totalValue, className="card-title"),
                        html.H6("New : " + str(newValue), className="card-subtitle")
                    ])
                 ], color = cardColor,inverse=True)
    return cardInfo


### App Layout
app.layout = html.Div(id='parent',
                      children=[navbar,
                                moving_info,
                                dbc.Row([
                                    dbc.Col(getCardInfo("Total Cases",confirmed,newconfirmed,"primary")),
                                    dbc.Col(getCardInfo("Total Recovered",recovered,newrecovered,"success")),
                                    dbc.Col(getCardInfo("Total Deaths",deaths,newdeaths,"danger"))
                                ]),
                                html.Br(),
                                dbc.Row([
                                    dbc.Col(dcc.Graph(id="world-Graph",figure=worldMap(df_world))),

                                    dbc.Col([html.Div(id = 'dropdown-div', children = 
                                                            [dcc.Dropdown(id = 'country-dropdown',
                                                                options = [{'label':i, 'value':i} for i in np.append(['All'],df_Countries['Country'].unique()) ],
                                                                value = 'All',
                                                                placeholder = 'Select the country',
                                                                multi= True
                                                                )], style = {'width':'100%', 'display':'inline-block'}),

                                            html.Div(id = 'world-table-output')
                                            ],style = {'height':'450px','text-align':'center'},xs = 12, sm = 12, md = 6, lg = 6, xl = 6)
                                    ])
                                ])

#
@app.callback(Output(component_id='world-table-output',component_property='children'),
              Input(component_id = 'country-dropdown' ,component_property = 'value'))
def tableInfo(countryValue):

    print(countryValue)
    if 'All' in countryValue or countryValue == 'All':
        dataframe = df_world
    else:
        dataframe = df_world.loc[df_world['Country'].isin(countryValue)]

    table = dash_table.DataTable(
                data = dataframe.to_dict('records'),
                columns = [{'id': i, 'name':i} for i in dataframe.columns],
                fixed_rows= {'headers':True},
                sort_action='native',
                style_table= {'maxHeight':'400px'},
                style_header= {'backgroundColor':'rgb(224,224,224)',
                                'fontWeight':'bold',
                                'border':'4px solid white',
                                'fontSize':'12px'
                                },
                style_cell = {'textAlign':'center',
                               'fontFamily':'Times New Roman',
                               'border':'4px solid white',
                               'maxWidth' :'50px',
                                'textOverflow': 'ellipsis',                            
                                }
            )
    return table


if __name__ == '__main__':
    app.run_server(debug=True,port='7272')
