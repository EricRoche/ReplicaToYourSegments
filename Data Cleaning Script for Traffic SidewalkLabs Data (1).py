
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np


# In[2]:


raw = pd.read_csv('NoModot.csv')


# In[3]:


#If the link_id has a link_id+1 present:
    #Then it has a pair (like east-west, or north-south shape pair) 
    #and is the first of the pair
#If the link_id does not have a link_id+1 present:
    #It is a second pair OR may be a street with only one traffic shape on it.
    #Could be a one-way, or other weird model fragments.
    #Deleting all of these results in missing streets
    #Keeping all of these results in a lot of duplicate line-segments
#If the link_Id+1 does not exist AND the link_id (not link_id+1) is odd, then it is a duplicate. 
    
#Let's operationalize this below.


# In[4]:


#Create a new dataframe to preserve the old one
df = raw.copy()
#keep only the necessary columns
df = df[['link_id', 'volume', 'geometry']]


# Let's first pull in the matching link_id's traffic volumes

# In[5]:


#create a link_id_plus column
df['link_id_plus'] = df.link_id + 1

#Create a seperate dataset that we will join to the main df
dftemp = df.copy()
dftemp = dftemp[['link_id_plus', 'volume']]
#rename the link_id_plus since it needs to be the same in both datasets to merge on
dftemp.columns = ['link_id', 'volume']

#Okay, let's merge this back in to the original dataset
df = pd.merge(df, dftemp, on='link_id', how='left')
#the merge sorts it weirdly, this makes it pretty again
df.sort_values(by=['link_id'], inplace=True)


# Find if there is a link_id_Plus_One match

# In[6]:


#Does the link_id_plus value exist as a link_id?
df["link_id_plus_exists"] = ""

#Use .isin to see if link_id_plus is in link_id. Returns true if it is.
df.link_id_plus_exists = df.link_id_plus.isin(df.link_id)


# Is the link_id odd?

# In[7]:


#create a link_id_is_odd column
df['link_id_is_even'] = ""

#Test if it is odd
df.link_id_is_even = (df.link_id & 1) == 0


# Let's add in some summary details

# In[8]:


#Average
df['mean_traffic_volume'] = df[["volume_x", "volume_y"]].mean(axis=1)
#StandardDeviation
df['standard_deviation_traffic_volume'] = df[["volume_x", "volume_y"]].std(axis=1)
#Replace all the NaNs with 
#df.fillna("")


# Let's label every observation as drop or keep

# In[9]:


#If link_id_plus_exists is TRUE  & link_id_is_even is TRUE  = keep it
#If link_id_plus_exists is FALSE & link_id_is_even is TRUE  = keep it
#If link_id_plus exists is FALSE & link_id_is_even is FALSE = Remove it
#if link_id_plus exists is True  & link_id_is_even is FALSE = Remove it

#Drop Column
df['drop_this_observation'] = ""

#This code takes the logic in the first cell comment and labels each observation as drop or keep.
df.drop_this_observation = np.where(
    ((df['link_id_plus_exists']==False) & (df['link_id_is_even']==False)) |
    ((df['link_id_plus_exists']==True) & (df['link_id_is_even']==False)), 'Drop','Keep')


# Let's now drop all of the observations labeled Drop

# In[10]:


df = df[df.drop_this_observation != 'Drop']


# The df should now be clean enough to bring back into arcgis and merge it with the shapefile. 
# If you use an "add join" and unselect all features it will only keep the ones in this dataset.
# Join on the LinkID field.
# 
# Finally, we will export this as a csv

# In[11]:


df.to_csv('final_clean_street_traffic_volume_segments.csv')

