import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import datetime

from google.colab import files

import plotly.figure_factory as ff
import plotly.graph_objects as go


STORE_NAME = input("Please enter store name: ")
print("Please upload Sponsored Products Campaign data as a csv file")
uploaded = files.upload()

for fn in uploaded.keys():

  print('User uploaded file "{name}" with length {length} bytes'.format(name=fn, length=len(uploaded[fn])))

#Get data
filename = list(uploaded.keys())[0]
data = pd.read_csv(filename)
data.index = pd.to_datetime(pd.to_datetime(data['Start Date'] + ' ' + data['Start Time'].astype(str) + ':00').dt.strftime('%Y-%m-%d %H:%M:%S'))
data['7 Day Total Sales '] = data['7 Day Total Sales '].str.replace('$', '').str.replace('.', '').astype('float32')/100


def get_hourly_heatmap():
  # Get globals
  START_DATE = pd.to_datetime(data['Start Date'], dayfirst=True).min().date()
  END_DATE = pd.to_datetime(data['Start Date'], dayfirst=True).max().date()
  
  data['hour'] = data.index.hour
  def create_heatmap_data(column):
      return data.groupby(['hour', data.index.day])[column].sum().unstack()
  
  z_impressions = create_heatmap_data('Impressions')
  z_clicks = create_heatmap_data('Clicks')
  z_orders = create_heatmap_data('7 Day Total Orders (#)')
  
  # x and y axis labels
  x_labels = data.index.day.unique().dropna().sort_values().values.astype(str)
  y_labels = data.index.hour.unique().dropna().values.astype(str)
  
  
  
  ## Create buttons for updating heatmap and annotations
  buttons = [
      dict(label="Impressions",
           method="update",
           args=[{
               "z": [z_impressions.values],
               'title': f'{STORE_NAME} Impressions Heatmap'
           }]),
      dict(label="Clicks",
           method="update",
           args=[{
               "z": [z_clicks.values],
               'title': f'{STORE_NAME} Clicks Heatmap'
           }]),
      dict(label="Orders",
           method="update",
           args=[{
               "z": [z_orders.values],
               'title': f'{STORE_NAME} Orders Heatmap'
           }])
  ]
  
  # Create initial heatmap figure
  fig = go.Figure(go.Heatmap(z=z_impressions.values,
                             x=x_labels,
                             y=y_labels,
                             colorscale="rdbu",
                             showscale=True))
  
  # Apply the default annotations for "Impressions" and other settings
  fig.update_layout(
      height=750,
      width=1200,
          updatemenus=[
          dict(
              type="buttons",
              showactive=True,
              buttons=buttons
          ) ],   
  
      title='Impressions Heatmap',
  
  )
  
  fig.update_yaxes(title_text="Hours", tickvals=np.arange(len(y_labels)), ticktext=y_labels)
  fig.update_xaxes(title_text="Days", tickvals=list(range(len(x_labels))), ticktext=x_labels)
  
  fig.show()
  return None

