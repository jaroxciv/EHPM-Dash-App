import pandas as pd
import geopandas as gpd
import geofeather as gf
import numpy as np
import os
import copy
import base64
import json
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly
import plotly.express as px
from flask import Flask

# API keys and datasets
mb_token = 'pk.eyJ1IjoiamF2aS1hbGZhcm8iLCJhIjoiY2tiMnR0cm5zMDBoejJ4cWNxb3Bzcno5aiJ9.Zh0OEJmyiH27YG4Yw_KLyg'
map_shape = gpd.read_file('./data/slv_adm2/SLV_adm2.shp')
map_shape.columns = map(str.lower, map_shape.columns)
map_shape['codigomunic'] = map_shape.name_2
map_shape['depto'] = map_shape.name_1   

gdf = gf.from_geofeather('./data/ehpm19_merged_sample.feather')
gdf.crs = "EPSG:4326" 
map_data = gdf.copy()
map_data["lon"] = gdf.centroid.x
map_data["lat"] = gdf.centroid.y

del gdf

# Preparing geojson
map_shape.to_file("./data/esa.json", driver = "GeoJSON")

with open('./data/esa.json') as response:
    esa_geoj = json.load(response)

px.set_mapbox_access_token(mb_token)

fig1 = px.choropleth_mapbox(map_data, geojson=esa_geoj, 
                    locations='codigomunic', featureidkey = "properties.codigomunic" ,
                    color='aproba1', 
                    color_continuous_scale=px.colors.sequential.RdBu,
                    range_color=(map_data.aproba1.min(), map_data.aproba1.max()),
                    labels={'aproba1':'Años aprobados'},
                    center={"lat": map_data.lat.mean(), "lon": map_data.lon.mean()},
                    zoom=7 #mapbox_style="streets"
                    )
fig1.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
#fig.show()

#fig2 = px.histogram(gdf, x="aproba1", color="r104", marginal='violin')

external_stylesheets = ['https://codepen.io/amyoshino/pen/jzXypZ.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'EHPM'

image_filename = "/content/drive/My Drive/EHPM/ehpm.png" # replace with your own image
encoded_image = base64.b64encode(open(image_filename, 'rb').read())

#temp = map_data.iloc[:,:-4]
#temp = map_data.loc[:, map_data.columns.isin(['aproba1', 'r104', 'ingre', 'pobreza', 'segm', 'r106', 'r107', 'ingfa', 'gastohog'])]
temp = {i for i in map_data[['aproba1', 'r104', 'ingre', 'pobreza', 'segm', 'r106', 'r107', 'ingfa', 'gastohog']].columns}
#all_options = temp.to_dict('records')[0]

#temp2 = map_data.loc[:, map_data.columns.isin(['aproba1', 'ingre', 'r106', 'ingfa', 'gastohog'])]
temp2 = {i for i in map_data[['aproba1', 'ingre', 'r106', 'ingfa', 'gastohog']].columns}
#numeric_options = temp2.to_dict('records')[0]

#temp3 = map_data.loc[:, map_data.columns.isin(['aproba1', 'ingre', 'r106', 'ingfa', 'gastohog','codigomunic'])].sample(frac=0.25)
temp3 = map_data[['aproba1', 'r104', 'ingre', 'pobreza', 'segm', 'r106', 'r107', 'ingfa', 'gastohog', 'depto', 'codigomunic']]

app.layout = html.Div(
    html.Div(
        [
         html.Div(
             [
              html.H1(children='EHPM 2019',
                      className='nine columns'),
                html.Img(
                    src='data:image/png;base64,{}'.format(encoded_image.decode()),
                    className='three columns',
                    style={
                        'height': '30%',
                        'width': '30%',
                        'float': 'right',
                        'position': 'relative',
                        'margin-top': 10,
                    },
                ),
              html.Div(children='''Visualización básica de variables.''',
                       className='nine columns'
                       )
              ], className="row"
              ),

        html.Div([
                  html.Div([
                            html.P('Elija la variable para el mapa:'),
                            dcc.RadioItems(
                                id = 'vars',
                                options=[{'label': k, 'value': k} for k in temp],
                                value='aproba1',
                                labelStyle={'display': 'inline-block'}
                                ),
                            ], 
                           className='seven columns', 
                           style={'margin-top': '10'}
                  ),
              
                # hist
                ],
                 className="row"
                 ),

        html.Div([
                  html.Div([
                            dcc.Graph(
                                id='map',
                                figure=fig1
                                )
                            ], className= 'twelve columns'
                  ),
            # html.Div(
            #         [
            #          dash_table.DataTable(
            #              id='datatable',
            #              columns=[{"name": i, "id": i} for i in sorted(temp.columns)],
            #                       page_current=0,
            #                       page_size=10,
            #                       page_action="custom"
            #                       )
            #          ],
            #          className="six columns"
            #          ),
        
        html.Div([
                  html.P('Variable para histograma'),
                  dcc.RadioItems(
                      id='numvars',
                      options=[{'label': k, 'value': k} for k in temp2],
                      value='aproba1',
                      labelStyle={'display': 'inline-block'}
                      ),
                  ],
                 className='six columns',
                 style={'margin-top': '10'}
                 ),

             html.Div([
                       dash_table.DataTable(
                           id='datatable',
                           columns=[{"name": i, "id": i, "deletable":True, "selectable":True} for i in temp3.columns],
                           page_current=0,
                           page_size=10,
                           page_action="native",
                           data=temp3.to_dict('records'),
                           filter_action="native",
                           selected_rows=[],
                           selected_columns=[]
                           ),
                           html.Div(id='datatable-interactivity-container')
                       ], className= 'twelve columns'
                       ),
             
             html.Div([
                       html.P('JA - ', style = {'display': 'inline'}),
                       html.A('javi.alfaro94@gmail.com', href = 'mailto:javi.alfaro94@gmail.com')
                       ],
                      className = "twelve columns",
                      style = {'fontSize': 18, 'padding-top': 20}
                      )
             ],
             className="row"
             )
        ],
        className='ten columns offset-by-one')
    )
 

@app.callback(
    Output('map', 'figure'),
    [Input('vars', 'value')]
    )
def update_map(variable):

  gdff = map_data.copy()
  #['aproba1', 'r104', 'ingre', 'pobreza', 'segm', 'r106','r107', 'ingfa', 'gastohog', 'codigomunic','geometry']
  if variable in ['aproba1', 'ingre', 'r106', 'ingfa', 'gastohog']:
    fig = px.choropleth_mapbox(gdff, geojson=esa_geoj, 
                      locations='codigomunic', featureidkey = "properties.codigomunic" ,
                      color=variable, 
                      color_continuous_scale=px.colors.sequential.RdBu,
                      range_color=(gdff[variable].min(), gdff[variable].max()),
                      labels={variable},
                      center={"lat": gdff.lat.mean(), "lon": gdff.lon.mean()},
                      zoom = 7 #mapbox_style="streets"
                      )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

  elif variable in ['segm', 'r107']:
    fig = px.choropleth_mapbox(gdff.dropna(subset=['segm', 'r107']), geojson=esa_geoj, 
                      locations='codigomunic', featureidkey = "properties.codigomunic" ,
                      color=variable,
                      color_discrete_sequence=px.colors.sequential.RdBu, 
                      labels={variable},
                      center={"lat": gdff.lat.mean(), "lon": gdff.lon.mean()},
                      zoom = 7 #mapbox_style="streets"
                      )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

  return fig

# @app.callback(
#     Output('bar', 'figure'),
#     [Input('numvars', 'value')]
#     )
# def update_figure(value):
#     gdff = map_data.copy()

#     fig = px.histogram(gdff, x=value, color="r104", marginal='violin')

#     return fig


# @app.callback(
#     Output('datatable', 'data'),
#     [Input('datatable', "page_current"),
#      Input('datatable', "page_size")])
# def update_table(page_current, page_size):
#     return temp.iloc[page_current*page_size:(page_current+ 1)*page_size].to_dict('records')

@app.callback(
    Output('datatable', 'style_data_conditional'),
    [Input('datatable', 'selected_columns')]
)
def update_styles(selected_columns):
    return [{'if': { 'column_id': i }, 'background_color': '#D2F3FF'} for i in selected_columns]

@app.callback(
    Output('datatable-interactivity-container', "children"),
    [Input('datatable', "derived_virtual_data"),
     Input('datatable', "derived_virtual_selected_rows")])
def update_graphs(rows, derived_virtual_selected_rows):
    # When the table is first rendered, `derived_virtual_data` and
    # `derived_virtual_selected_rows` will be `None`. This is due to an
    # idiosyncracy in Dash (unsupplied properties are always None and Dash
    # calls the dependent callbacks when the component is first rendered).
    # So, if `rows` is `None`, then the component was just rendered
    # and its value will be the same as the component's dataframe.
    # Instead of setting `None` in here, you could also set
    # `derived_virtual_data=df.to_rows('dict')` when you initialize
    # the component.
    if derived_virtual_selected_rows is None:
        derived_virtual_selected_rows = []

    dff = temp3 if rows is None else pd.DataFrame(rows)

    colors = ['#7FDBFF' if i in derived_virtual_selected_rows else '#0074D9' for i in range(len(dff))]
    
    gdff = temp3.copy()

    return [
        dcc.Graph(
            id=column,
            figure=px.histogram(gdff, x="depto", y=column, 
                          title=None,
                           color='r104',
                           histfunc='count',
                           histnorm='percent',
                           cumulative=False,
                           color_discrete_sequence=['#879ea6', '#404352']
                          ),
        )
        # check if column exists - user may have deleted it
        # If `column.deletable=False`, then you don't
        # need to do this check.
        for column in ['aproba1', 'ingre', 'r106', 'ingfa', 'gastohog'] #if column in dff
    ]

if __name__ == '__main__':
    app.run_server(debug=True)
