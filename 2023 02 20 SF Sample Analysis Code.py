#!/usr/bin/env python
# coding: utf-8

# In[1]:


#Import libraries
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')


# In[2]:


#Load in student data and examine
student_df = pd.read_csv('Sample Data for Analysis.xlsx - Raw Data.csv')
student_df.info() 


# In[3]:


#Count number of missing values for GEOID
student_df['GEOID'].value_counts(dropna=False)[np.nan]


# In the Student dataset, we are missing 127 values of GEOID. This is about .7% of the data. This will be addressed in the following steps.

# In[4]:


#Assemble a new dataframe that finds the most frequent GEOID for each city-state pair.
#This will be used to impute missing GEOIDs
city_geoid_df = student_df[['City','State','GEOID']]
city_common_geoid_df = city_geoid_df.groupby(['City','State']).GEOID.agg(pd.Series.mode).to_frame()


# In[5]:


#examine common GEOIDs
city_common_geoid_df['GEOID'] = city_common_geoid_df['GEOID'][0]
city_common_geoid_df


# In[6]:


#Merge the student dataframe with the GEOID mode dataframe
df = student_df.merge(city_common_geoid_df, how='left', left_on=['City', 'State'], right_on=['City', 'State'])
df = df.rename(columns={'GEOID_x': 'GEOID', 'GEOID_y': 'City_GEOID_mode'})


# In[7]:


#Count of nan values before imputation
df['GEOID'].value_counts(dropna=False)[np.nan]


# In[8]:


#Impute missing GEOID values with the highest frequency GEOID per city-state pair
df['GEOID'].fillna(value=df['City_GEOID_mode'], inplace=True)


# In[9]:


#Count of na values after GEOID imputation
na_values = df[df['GEOID'] == np.nan]
len(na_values)


# We have now handled the NA values from this source.

# In[10]:


#Read distance csv
distance_df = pd.read_csv('Sample Data for Analysis.xlsx - Distances to Campus.csv')
distance_df.head()


# In[11]:


#map campus names for join with the main dataframe df
distance_df['Campus'] = distance_df['Campus'].map({'East Campus':'ETC','Main Campus':'MNC','West Campus':'WTC', 'Online':'WEB'})
distance_df.head()


# In[12]:


#Merge dataframe with the distance table. This associates each student with their distance from campus.
#The students that didn't have a GEOID associated with them were assigned the most frequent
#GEOID in their city-state pair.
combined_df = df.merge(distance_df, how='left',left_on=['GEOID', 'Campus'], right_on=['GEOID', 'Campus'])
#check the number of na values after merging. This would attribute to GEOIDs that don't have a distance mapping
len(combined_df[combined_df['Distance'].isna()])


# In[13]:


null_df = combined_df[combined_df['Distance'].isna()]
null_df['x'] = null_df['Distance'].isnull()
null_df = null_df.groupby('State')['x'].sum()
null_df


# From this, we find that we still have a lot of GEOIDs that do not have distance listed. These are attributed to online students. Since the majority of these students still live in MO, we will attempt to solve this by calculating the average distance for each city-state pair, and then assign the average distance to the missing distances for that particular city.
# 
# This method will use average distance from a campus based on the student's city-state pair.

# In[14]:


#Calculate average distance in each city-state pair
avg_distance_df = combined_df.groupby(['City', 'State'])['Distance'].mean().to_frame()
avg_distance_df = avg_distance_df.rename(columns={'Distance':'avg_distance'})
avg_distance_df


# In[15]:


combined_df = combined_df.merge(avg_distance_df, left_on=['City','State'], right_on=['City','State'])
combined_df['Distance'].fillna(value=combined_df['avg_distance'], inplace=True)
combined_df


# In[16]:


#Drop remaining Nan values from combined_df
print(len(combined_df))
combined_df = combined_df.dropna()
print(len(combined_df))


# After replacing the missing distances with the average distance in each city, we were able to reduce the Nan values from 5493 to 344. These remaining can be dropped without significant impact to the analysis.

# In[17]:


binned_df = combined_df
bins = [0,20,40,60,80,100,120,140,160,180,200,220,240,260,280,300,10000]
labels = ['0-20','20-40','40-60','60-80','80-100','100-120','120-140','140-160','160-180','180-200','200-220','220-240','240-260','260-280','280-300','>300']
binned_df['Miles'] = pd.cut(binned_df['Distance'], bins=bins, labels=labels, include_lowest=True).to_frame()
binned_df


# In[18]:


binned_df = binned_df.drop(columns=['Degree Level','CIP Code', 'Program Title', 'City', 'State', 'GEOID', 'City_GEOID_mode','Distance','avg_distance'])
binned_df


# In[19]:


pivot_df = binned_df.pivot_table(columns='Campus', values='STUDENTS', index='Miles', aggfunc='count')
pivot_df = pivot_df.reindex(labels)
pivot_df = pivot_df.fillna(value=0)
total = len(combined_df)
for col in pivot_df.columns:
    pivot_df[col] = pivot_df[col]/total
pivot_df


# In[20]:


pivot_df['Total'] = pivot_df['ETC'] + pivot_df['MNC'] + pivot_df['WEB'] + pivot_df['WTC']
pivot_df


# In[21]:


pivot_df.to_csv('pivot_frame.csv')


# <h1>Assumptions to Address</h1>
# There were two main problems to handle during this analysis; 1.) How do you handle students without a GEOID, and 2.) How do you handle GEOIDs that don't have mapped distances. Following, I will address how I approached each of these.
# 
# <h3>Students with missing GEOIDs</h3>
# I approached this by counting the occurences of GEOIDs in each city-state pair, and creating a dataframe assigning the mode of the GEOID to each city-state pair. This is done in cell 4. Then, I joined the original dataframe with this GEOID mode dataframe, and filled the NA values of student GEOID with the GEOID mode.
# 
# <h3>GEOIDs with missing distances</h3>
# This was a far more pervasive problem than the previous, affecting nearly 5500 students, largely due to online students (see below). I approached this problem by calculating the average distance from campus for each city-state pair, creating a dataframe holding each city and state with it's associated average distance. Then, I joined the student dataframe with this distance dataframe on City and State and imputed the average distance on the missing distances.
# 
# <h3>Online Students</h3>
# My first thought was that the distances for online students was not something to be considered, but upon thinking on it more, and due to the locations of many of the online students, this could not be done. The majority of the online students live in Springfield, or MO, for that matter. My assumption is that being an online student does not preclude being a student that visits a campus, and while I don't know the details of the dataset or the use case of this analysis, I found it desirable to also include online students' locations. 

# <h1>Improvements</h1>
# 
# Looking forward, there are a few improvements to be made:
#     
# 1.) Higher Precision bins could be used. Particularly useful in the nearby radii, smaller bins would tell a deeper story about have students are distributed around each campus.
#     
# 2.) GEOIDs to be imputed could come from the distribution of GEOIDs. So, instead of just considering the mode, a GEOID could be chosen by a random number generator using the value counts of GEOID in each city-state combination. This could lead to higher accuracy during the binning process. 
#     
# 3.) Similar to the improvement above, instead of just using the average distance in each city, a random generator could be used to pick a distance based on the value counts in each city. This would also allow for a deeper understanding of where students without distances could be coming from.
