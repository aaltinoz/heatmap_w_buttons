import dash
from dash import dcc,html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from jupyter_dash import JupyterDash
import datetime
from datetime import datetime
from google.colab import files






def run_dash_app():
  STORE_NAME = input("Please enter store name: ")
  print("Please upload Sponsored Products Campaign data as a csv file")
  uploaded = files.upload()

  for fn in uploaded.keys():

    print('User uploaded file "{name}" with length {length} bytes'.format(name=fn, length=len(uploaded[fn])))

  # # #Get data
  filename = list(uploaded.keys())[0]
  data = pd.read_csv(filename)
    # preprocess
  data['time'] = data.iloc[:, 2]
  data.index = pd.to_datetime(
      pd.to_datetime(data['Start Date'] + ' ' + data['time'].astype(str) + ':00').dt.strftime('%m/%d/%Y %H:%M:%S'))
  data['Sales'] = data.iloc[:, 20]
  data['Sales'] = data['Sales'].str.replace('£', '').str.replace('$', '').str.replace('.', '').astype('float32') / 100
  data['spend'] = data.iloc[:, 15]
  data['spend'] = data['spend'].str.replace('£', '').str.replace('$', '').str.replace('.', '').astype('float32') / 100
  data['hour'] = data.index.hour
  data['groupby_col'] = data.index.to_series().dt.strftime('%b/%d')
  data['Orders'] = data.iloc[:, 17]
  START_DATE = (pd.to_datetime(data['Start Date']).min()).strftime('%b/%d/%y')
  END_DATE = (pd.to_datetime(data['Start Date']).max()).strftime('%b/%d/%y')
  y_labels = data.index.hour.unique().dropna().values.astype(str)

  app = dash.Dash(__name__)

  app.layout = html.Div([
      dcc.Dropdown(
          id='campaign-dropdown',
          options=[{'label': 'All Campaigns', 'value': 'All'}] + [{'label': i, 'value': i} for i in
                                                                  data['Campaign Name'].unique()],
          value='All',
          multi=False,
          style={"fontFamily": "Oswald", "fontSize": "18px"}
      ),
      dcc.RadioItems(
          id='metric-radio',
          options=[{'label': i, 'value': i} for i in ['Impressions', 'Clicks', 'spend', 'Sales', 'Orders']],
          value='Impressions',
          style={"fontFamily": "Oswald", "fontSize": "18px"}
      ),
      dcc.Graph(id='heatmap'),
  ])


  @app.callback(
      Output('heatmap', 'figure'),
      [Input('campaign-dropdown', 'value'),
      Input('metric-radio', 'value')]
  )
  def update_figure(selected_campaign, selected_metric):
      # Filter data based on dropdown
      if selected_campaign != "All":
          filtered_data = data[data['Campaign Name'] == selected_campaign]
      else:
          filtered_data = data

      heatmap_data = filtered_data.pivot_table(index='hour', columns='groupby_col', values=selected_metric, aggfunc='sum')
      heatmap_data = heatmap_data[sorted(np.unique(data.groupby_col.values), key=lambda x: datetime.strptime(x, '%b/%d'))]

      fig = go.Figure(data=go.Heatmap(
          z=heatmap_data.values,
          x=heatmap_data.columns.tolist(),
          y=heatmap_data.index.tolist(),
          colorscale='RdBu'
      ))
      fig.update_layout(title=f'{STORE_NAME} {selected_metric} Heatmap {START_DATE} - {END_DATE}',
                        xaxis_title='Date',
                        yaxis_title='Hour of Day',
                        width=1000,
                        height=600,
                        font=dict(
                            family='Roboto'
                        )
                        )
      fig.update_yaxes(title_text="Hours", tickvals=np.arange(len(y_labels)), ticktext=y_labels)
      fig.update_xaxes(title_text="Days",
                      tickvals=sorted(np.unique(data.groupby_col.values), key=lambda x: datetime.strptime(x, '%b/%d')),
                      ticktext=sorted(np.unique(data.groupby_col.values), key=lambda x: datetime.strptime(x, '%b/%d')))
      return fig

  
  app.run(jupyter_mode='external')

  
