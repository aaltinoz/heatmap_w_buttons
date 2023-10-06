import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
import warnings
warnings.filterwarnings("ignore")


from google.colab import files

import plotly.figure_factory as ff
import plotly.graph_objects as go


STORE_NAME = input("Please enter store name: ")
print("Please upload Sponsored Products Campaign data as a csv file")
uploaded = files.upload()

for fn in uploaded.keys():

  print('User uploaded file "{name}" with length {length} bytes'.format(name=fn, length=len(uploaded[fn])))

# # #Get data
filename = list(uploaded.keys())[0]
data = pd.read_csv(filename)

data['time'] = data.iloc[:,2]
data.index = pd.to_datetime(pd.to_datetime(data['Start Date'] + ' ' + data['time'].astype(str) + ':00').dt.strftime('%m/%d/%Y %H:%M:%S'))
data['Sales'] = data.iloc[:,20]
data['Sales'] = data['Sales'].str.replace('£', '').str.replace('$', '').str.replace('.', '').str.replace(',','').astype('float32')/100
data['spend'] = data.iloc[:,15]
data['spend'] = data['spend'].str.replace('£', '').str.replace('$', '').str.replace('.', '').str.replace(',','').astype('float32')/100
data['hour'] = data.index.hour


def get_hourly_heatmap():
  # Get globals
  START_DATE = (pd.to_datetime(data['Start Date']).min()).strftime('%b/%d/%y')
  END_DATE =(pd.to_datetime(data['Start Date']).max()).strftime('%b/%d/%y')



  def create_heatmap_data(column, data_to_use):
      return data_to_use.groupby(['hour', data_to_use.index.day])[column].sum().unstack()

  #Apply Function
  z_impressions = create_heatmap_data('Impressions',data)
  z_clicks = create_heatmap_data('Clicks',data)
  z_orders = create_heatmap_data('7 Day Total Orders (#)',data)
  z_spend = create_heatmap_data('spend', data)
  z_sales = create_heatmap_data('Sales', data)


  # x and y axis labels
  x_labels = data.index.day.unique().dropna().sort_values().values.astype(str)
  y_labels = data.index.hour.unique().dropna().values.astype(str)

  # Sort Dates
  sorted_dates = np.unique(data.index.date)
  formatted_dates = [date.strftime('%b/%d') for date in sorted_dates]
  
  # Define a function to generate a hover template based on the metric name
  def generate_hover_template(metric_name):
      return f"Day: %{{x}}<br>Hours: %{{y}}<br>{metric_name}: %{{z}}"

  # Metric Buttons
  metric_buttons = [
    dict(label="Impressions",
         method="update",
         args=[{"z": [z_impressions.values],
                "hovertemplate": generate_hover_template("Impressions")},
               {"title": f'{STORE_NAME} Impressions Heatmap {START_DATE} - {END_DATE}'}]),
    dict(label='Sales',
         method='update',
         args=[{'z': [z_sales.values],
                "hovertemplate": generate_hover_template("Sales")},
               {"title": f'{STORE_NAME} Sales Heatmap {START_DATE} - {END_DATE}'}]),
    dict(label="Clicks",
         method="update",
         args=[{"z": [z_clicks.values],
                "hovertemplate": generate_hover_template("Clicks")},
               {"title": f'{STORE_NAME} Clicks Heatmap {START_DATE} - {END_DATE}'}]),
    dict(label="Orders",
         method="update",
         args=[{"z": [z_orders.values],
                "hovertemplate": generate_hover_template("Orders")},
               {"title": f'{STORE_NAME} Orders Heatmap {START_DATE} - {END_DATE}'}]),
    dict(label='Spend',
         method='update',
         args=[{'z': [z_spend.values],
                "hovertemplate": generate_hover_template("Spend")},
               {"title": f'{STORE_NAME} Spend Heatmap {START_DATE} - {END_DATE}'}])
    ]


  # Dropdown for campaigns
  campaign_dropdown = []

  # Add a "None" option to the dropdown to reset the filter
  none_option = dict(
      args=[{"z": [z_impressions.values], "title": f"{STORE_NAME} Impressions Heatmap {START_DATE} - {END_DATE}"}],
      label="All Campaigns",
      method="update"
  )
  campaign_dropdown.append(none_option)

  # Getting Campaign names
  campaign_names = data['Campaign Name'].unique()
  for campaign_name in campaign_names:
      filtered_data = data[data['Campaign Name'] == campaign_name]

      z_data_impressions = create_heatmap_data('Impressions', filtered_data)

      campaign_option = dict(
          args=[{"z": [z_data_impressions.values], "title": f"{STORE_NAME} Impressions Heatmap for Campaign: {campaign_name}"}],
          label=campaign_name,
          method="update"
      )

      campaign_dropdown.append(campaign_option)



  # Create heatmap figure
  fig = go.Figure(go.Heatmap(z=z_impressions.values,
                           x=formatted_dates,
                           y=y_labels,
                           colorscale="rdbu",
                           showscale=True,
                            name="",  # Set name as empty
                           showlegend=False,  # Ensure legend doesn't show
                           hovertemplate=generate_hover_template("Impressions")))

  fig.update_layout(
      height=750,
      width=1300,
      updatemenus=[
          # Metric buttons
          dict(
              type="buttons",
              buttons=metric_buttons,
              direction="down",
              showactive=True,
              x=1.10,
              y=1.015,
              xanchor='left',
              yanchor='top'
          ),
          # Campaign dropdown
          dict(
              buttons=campaign_dropdown,
              direction="down",
              showactive=True,
              x=0,
              y=1.07,
              xanchor='left',
              yanchor='top'
          )
      ],
      title= f'{STORE_NAME} Impressions Heatmap {START_DATE} - {END_DATE}'
  )


  fig.update_yaxes(title_text="Hours", tickvals=np.arange(len(y_labels)), ticktext=y_labels)
  fig.update_xaxes(title_text="Days", 
                 tickvals=np.arange(0, len(formatted_dates), 1),
                 ticktext=formatted_dates)

  fig.show()
  return None
