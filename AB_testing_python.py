# -*- coding: utf-8 -*-


#import pandas
import pandas as pd

#import csv data
ad_clicks = pd.read_csv('ad_clicks.csv')

#count views from each source
ad_count = ad_clicks.groupby('utm_source').user_id.count().reset_index()

#print(ad_count)

#create df column for if ad was clicked
ad_clicks['is_click'] = ~ad_clicks.ad_click_timestamp.isnull()

#group by clicks from each source
clicks_by_source = ad_clicks.groupby(['utm_source','is_click']).user_id.count().reset_index()

#pivot table
clicks_pivot = clicks_by_source.pivot(
  columns='is_click',
  index='utm_source',
  values='user_id'
)

#new column in pivot table for percentage of clicks
clicks_pivot['percent_click'] = 100* clicks_pivot[True]/(clicks_pivot[True] + clicks_pivot[False])
print(clicks_pivot)

#count the users in each experimental group
count = ad_clicks.groupby('experimental_group').user_id.count().reset_index()

#check count
print(count)

#count users, grouping by group and is_click, and pivot, having columns is_click
check = ad_clicks.groupby(['experimental_group','is_click']).user_id.count().reset_index().pivot(
  index='experimental_group',
  columns='is_click',
  values='user_id'
).reset_index()

#separate dfs for each experimental group
a_clicks = ad_clicks[ad_clicks.experimental_group == 'A']
b_clicks = ad_clicks[ad_clicks.experimental_group == 'B']

#group by day, then pivot so columns show if the ad was clicked
a_clicks_pivot = a_clicks.groupby(['is_click','day']).user_id.count().reset_index().pivot(
  columns='is_click',
  index='day',
  values='user_id'
).reset_index()
#add percentage column
a_clicks_pivot['percent_clicked'] = 100 * a_clicks_pivot[True] / (a_clicks_pivot[True] + a_clicks_pivot[False])
print(a_clicks_pivot)

#repeat process for B group
b_clicks_pivot = b_clicks.groupby(['is_click','day']).user_id.count().reset_index().pivot(
  columns='is_click',
  index='day',
  values='user_id'
).reset_index()
b_clicks_pivot['percent_clicked'] = 100 * b_clicks_pivot[True] / (b_clicks_pivot[True] + b_clicks_pivot[False])
print(b_clicks_pivot)