# -*- coding: utf-8 -*-
"""DataStorm_Finals_Feature_Engineering.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1OTQm3_in1_wiDTiwhYI6t5E74vUf9jsu

##Import Libraries

###Neptune Ai
"""

! pip install neptune-client==0.4.132

pip install  neptune-contrib neptune-client

import neptune
from neptunecontrib.monitoring.keras import NeptuneMonitor
neptune.init(project_qualified_name='jathurshan0330/DataStorm2-finals', # change this to your `workspace_name/project_name`
             api_token='eyJhcGlfYWRkcmVzcyI6Imh0dHBzOi8vdWkubmVwdHVuZS5haSIsImFwaV91cmwiOiJodHRwczovL3VpLm5lcHR1bmUuYWkiLCJhcGlfa2V5IjoiZmJkZjYxNGYtMTA0ZC00ZTc1LWJiMTYtNzczNjgwZWQ3OTUzIn0=', # change this to your api token
            )

"""### Other Libraries"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.io
import seaborn as sns
from sklearn.model_selection import train_test_split
import tensorflow as tf
from scipy import stats 
from tensorflow.keras.models import Sequential,Model
from tensorflow.keras.layers import Dense, Input,LSTM,Reshape,Conv2D,Flatten,Dropout,BatchNormalization, LeakyReLU, concatenate, GRU, GlobalMaxPooling1D, GlobalMaxPooling2D, Bidirectional

!pip install scikit-plot

"""##Read Data

###Mount Drive
"""

from google.colab import drive
drive.mount('/content/drive')

cd '/content/drive/My Drive/Datastorm2.0_Final'

!ls '/content/drive/My Drive/Datastorm2.0_Final'

"""###Data"""

agent_data = pd.read_csv('datastorm_agent_data.csv')
print(agent_data.head()) 
print(agent_data.shape)
print(agent_data.columns)

policy_data = pd.read_csv('datastorm_policy_data.csv')
print(policy_data.head()) 
print(policy_data.shape)
print(policy_data.columns)


test_data = pd.read_csv('testset.csv')
print(test_data.head())
print(test_data.shape)
print(test_data.columns)

print("Agent Data")
print(agent_data.isna().sum())
print('\n')
print("Policy Data")
print(policy_data.isna().sum())
print('\n')
print("Test Data")
print(test_data.isna().sum())

"""##Data Preprocessing

###One hot Encoding
"""

print(policy_data.shape)
print(policy_data.columns)

def getting_dummies(main_data,column_name, pre, drop = True):
  dummies = pd.get_dummies(main_data[column_name],drop_first=drop, prefix= pre)
  data = main_data.pop(column_name)
  main_data=pd.concat([main_data, dummies],axis=1)
  return main_data

policy_data = getting_dummies(policy_data, 'main_holder_gender', 'Gender',drop = True)

policy_data = getting_dummies(policy_data, 'policy_payment_mode', 'Pay_mode',drop = False)

policy_data = getting_dummies(policy_data, 'policy_status', 'status',drop = False)

policy_data = getting_dummies(policy_data, 'termination_reason', 'ter_reason',drop = False)

policy_data = getting_dummies(policy_data, 'main_holder_smoker_flag', 'main_smoker',drop = True)

policy_data = getting_dummies(policy_data, 'spouse_gender', 'Spouse_Gender',drop = False)

policy_data = getting_dummies(policy_data, 'spouse_smoker_flag', 'Spouse_smoker',drop = False)

policy_data = getting_dummies(policy_data, 'child1_gender', 'child1_gender',drop = False)

policy_data = getting_dummies(policy_data, 'child2_gender', 'child2_gender',drop = False)

policy_data = getting_dummies(policy_data, 'child3_gender', 'child3_gender',drop = False)

policy_data = getting_dummies(policy_data, 'child4_gender', 'child4_gender',drop = False)

policy_data = getting_dummies(policy_data, 'child5_gender', 'child5_gender',drop = False)

policy_data = getting_dummies(policy_data, 'payment_method', 'payment_method',drop = False)


print(policy_data.shape)
print(policy_data.columns)

"""###Data Analysis"""

client = policy_data["client_code"]
client = client.tolist()
client = set(client)
#client = client.tolist()
client_2 = []
for i in client:
  client_2.append(i)
print(len(client))
print(len(client_2))

from datetime import datetime
def days(start_date, end_date):
  start_date = datetime.strptime(start_date, "%Y/%m/%d")
  end_date = datetime.strptime(end_date, "%Y/%m/%d")
  #print((end_date - start_date).days)
  return (end_date - start_date).days

from collections import Counter
client_policies = [[] for i in range (len(client))]
client_policy_num = [[] for i in range (len(client))]
for i in range(len(policy_data)):
  a = policy_data['product_name'][i]
  b = policy_data['policy_code'][i]
  c = policy_data['client_code'][i]
  #print(policy_data['commencement_dt'][i])
  #day_ = days('2018/12/31', policy_data['commencement_dt'][i])
  ind = client_2.index(c)
  #print(c)
  #print(ind)
  #print(day_)
  #if len(client_policy_num[ind]) == 0:
   # if b not in client_policy_num[ind]:
    #  client_policies[ind].append(a)
     # client_policy_num[ind].append(b)

  #elif day_>=0:
  if b not in client_policy_num[ind]:
    client_policies[ind].append(a)
    client_policy_num[ind].append(b)
      #break

print(len(client_policy_num))
print(len(client_policies))
count = []
for i in client_policy_num:
  count.append(len(i))
print(Counter(count))

count = []
for i in client_policies:
  i = set(i)
  count.append(len(i))
print(Counter(count))

print(client_policy_num[14890])
print(client_policies[14890])



"""## Feature Engineering

###Breaking data into three time period
"""

# Sort Dataframe
policy_data_sorted = policy_data.sort_values(by=['client_code','policy_snapshot_as_on'], ignore_index = True)

print(policy_data_sorted.shape)
print(policy_data_sorted['client_code'].head())
print(policy_data_sorted['policy_snapshot_as_on'].head())
policy_data_sorted.head()

policy_jan_jun_19 = []
policy_jul_dec_19 = []
policy_jan_jun_20 = []
column_names = policy_data_sorted.columns
first_6 = ['01','02','03','04','05','06']

for i in range(len(policy_data_sorted)):
  time = str(policy_data_sorted["policy_snapshot_as_on"][i])
  year = time[:4]
  month = time[4:6]
  date = time[6:]
  #print(time)
  #print(date)
  #print(month)
  #print(year)
  if year == '2019':
    if month in first_6:
      policy_jan_jun_19.append(policy_data_sorted.iloc[i])
    elif month == '07' and date == '01':
      policy_jan_jun_19.append(policy_data_sorted.iloc[i])
    else:
      policy_jul_dec_19.append(policy_data_sorted.iloc[i])
  elif year == '2020':
    if month =='01' and date == '01':
      policy_jul_dec_19.append(policy_data_sorted.iloc[i])
    else:
      policy_jan_jun_20.append(policy_data_sorted.iloc[i]) 
 # break

 
policy_jan_jun_19 = pd.DataFrame(policy_jan_jun_19)
policy_jan_jun_19 = policy_jan_jun_19.sort_values(by=['client_code','policy_snapshot_as_on'], ignore_index = True)
policy_jul_dec_19 = pd.DataFrame(policy_jul_dec_19)
policy_jul_dec_19 = policy_jul_dec_19.sort_values(by=['client_code','policy_snapshot_as_on'], ignore_index = True)
policy_jan_jun_20 = pd.DataFrame(policy_jan_jun_20)
policy_jan_jun_20 = policy_jan_jun_20.sort_values(by=['client_code','policy_snapshot_as_on'], ignore_index = True)

print(policy_jan_jun_19.shape)
print(policy_jul_dec_19.shape)
print(policy_jan_jun_20.shape)

policy_jan_jun_19.head()

policy_jul_dec_19.head()

policy_jan_jun_20.head()

#Save to Drive
policy_jan_jun_19.to_csv('policy_jan_jun_19.csv',index=False)
policy_jul_dec_19.to_csv('policy_jul_dec_19.csv',index=False)
policy_jan_jun_20.to_csv('policy_jan_jun_20.csv',index=False)

a=[]
a.append(policy_data_sorted.iloc[0])
a.append(policy_data_sorted.iloc[1])
a=pd.DataFrame(a)
a.head()

"""###Feature Extraction

"""

# Read previously saved data
policy_jan_jun_19 = pd.read_csv('policy_jan_jun_19.csv')
print(policy_jan_jun_19.head()) 
print(policy_jan_jun_19.shape)

policy_jul_dec_19= pd.read_csv('policy_jul_dec_19.csv')
print(policy_jul_dec_19.head()) 
print(policy_jul_dec_19.shape)

policy_jan_jun_20 = pd.read_csv('policy_jan_jun_20.csv')
print(policy_jan_jun_20.head()) 
print(policy_jan_jun_20.shape)

data_jan_jun_19 = []
for i in range(len(policy_jan_jun_19)): 
  x = policy_jan_jun_19['client_code'][i]
  if x not in data_jan_jun_19:
    data_jan_jun_19.append(x)
data_jan_jun_19 = pd.DataFrame(data_jan_jun_19, columns = ['client_code'])

print(len(data_jan_jun_19))
print(data_jan_jun_19.head())

data_jul_dec_19 = []
for i in range(len(policy_jul_dec_19)): 
  x = policy_jul_dec_19['client_code'][i]
  if x not in data_jul_dec_19:
    data_jul_dec_19.append(x)
data_jul_dec_19 = pd.DataFrame(data_jul_dec_19, columns = ['client_code'])

print(len(data_jul_dec_19))
print(data_jul_dec_19.head())

data_jan_jun_20 = []
for i in range(len(policy_jan_jun_20)): 
  x = policy_jan_jun_20['client_code'][i]
  if x not in data_jan_jun_20:
    data_jan_jun_20.append(x)
data_jan_jun_20 = pd.DataFrame(data_jan_jun_20, columns = ['client_code'])

print(len(data_jan_jun_20))
print(data_jan_jun_20.head())

from datetime import datetime
def days(start_date, end_date):
  start_date = datetime.strptime(start_date, "%Y/%m/%d")
  end_date = datetime.strptime(end_date, "%Y/%m/%d")
  #print((end_date - start_date).days)
  return (end_date - start_date).days

"""####Extracting Labels"""

#Extracting Labels for jan to june 2019 using jul to dec data
labels_jan_jun_19 = []
recom_jan_jun_19 = []
for i in range (len(data_jan_jun_19)):
  temp = policy_jul_dec_19[policy_jul_dec_19['client_code'] == data_jan_jun_19['client_code'][i]]
  temp = temp.sort_values(by=['client_code','policy_snapshot_as_on'], ignore_index = True)
  #print(temp)
  inforce_count = 0
  new_policy_count = 0
  new_policy = 'No_policy'
  for j in range (len(temp)):
    #print(temp['commencement_dt'][j])
    day_ = days('2019/06/30', temp['commencement_dt'][j])
    day_2 = days('2019/12/31', temp['commencement_dt'][j])
    #print(day_)
    if (temp['status_INFORCE'][j] == 1 or temp['status_LAPSED'][j] == 1)  and day_ <= 0:
      inforce_count+=1
    if (temp['status_INFORCE'][j] == 1 or temp['status_LAPSED'][j] == 1)  and day_ > 0 and day_2 <= 0:
      new_policy_count+=1
      new_policy = temp['product_name'][j]
    if inforce_count >=1 and new_policy_count >=1 :
      break
  
  if inforce_count > 0 and new_policy_count > 0:
    labels_jan_jun_19.append(1)
    recom_jan_jun_19.append(new_policy)
  else:
    labels_jan_jun_19.append(0)
    recom_jan_jun_19.append('No_policy')

labels_jan_jun_19 = pd.DataFrame(labels_jan_jun_19, columns = ['cross_sell'])
labels_jan_jun_19 = pd.concat([data_jan_jun_19,labels_jan_jun_19],axis=1)

recom_jan_jun_19 = pd.DataFrame(recom_jan_jun_19, columns = ['recommentation'])
labels_jan_jun_19 = pd.concat([labels_jan_jun_19, recom_jan_jun_19],axis=1)

print(labels_jan_jun_19.shape)
labels_jan_jun_19.head()

print(Counter(labels_jan_jun_19['cross_sell']))
print(Counter(labels_jan_jun_19['recommentation']))

labels_jan_jun_19.to_csv('labels_jan_jun_19.csv',index=False)

#Extracting Labels for july to dec 2019 using jan to june 2020 data
labels_jul_dec_19 = []
recom_jul_dec_19 = []
for i in range (len(data_jul_dec_19)):
  temp = policy_jan_jun_20[policy_jan_jun_20['client_code'] == data_jul_dec_19['client_code'][i]]
  temp = temp.sort_values(by=['client_code','policy_snapshot_as_on'], ignore_index = True)
  #print(temp)
  inforce_count = 0
  new_policy_count = 0
  new_policy = 'No_policy'
  for j in range (len(temp)):
    #print(temp['commencement_dt'][j])
    day_ = days('2019/12/31', temp['commencement_dt'][j])
    day_2 = days('2020/6/30', temp['commencement_dt'][j])
    #print(day_)
    if (temp['status_INFORCE'][j] == 1 or temp['status_LAPSED'][j] == 1)  and day_ <= 0:
      inforce_count+=1
    if (temp['status_INFORCE'][j] == 1 or temp['status_LAPSED'][j] == 1)  and day_ > 0 and day_2 <= 0:
      new_policy_count+=1
      new_policy = temp['product_name'][j]
    if inforce_count >=1 and new_policy_count >=1 :
      break
  
  if inforce_count > 0 and new_policy_count > 0:
    labels_jul_dec_19.append(1)
    recom_jul_dec_19.append(new_policy)
  else:
    labels_jul_dec_19.append(0)
    recom_jul_dec_19.append('No_policy')

labels_jul_dec_19 = pd.DataFrame(labels_jul_dec_19, columns = ['cross_sell'])
labels_jul_dec_19 = pd.concat([data_jul_dec_19,labels_jul_dec_19],axis=1)

recom_jul_dec_19 = pd.DataFrame(recom_jul_dec_19, columns = ['recommentation'])
labels_jul_dec_19 = pd.concat([labels_jul_dec_19, recom_jul_dec_19],axis=1)

print(labels_jul_dec_19.shape)
labels_jul_dec_19.head()

print(Counter(labels_jul_dec_19['cross_sell']))
print(Counter(labels_jul_dec_19['recommentation']))

labels_jul_dec_19.to_csv('labels_jul_dec_19.csv',index=False)

"""####Features"""

from datetime import datetime
def age(date,date2):
  year = datetime.strptime(date, "%Y/%m/%d").year
  new_year = datetime.strptime(date2, '%Y%m%d').year
  return new_year-year

# extracting features for jan to june
# policy_term_avg, Pay_mode_H,	Pay_mode_M,	Pay_mode_Q,	Pay_mode_S,	Pay_mode_Y, main_smoker, spouse_smoker, inforce_count, lapse_count, terminate_count, lap_inf_ratio, ter_inf_ratio, num_children, num_policies, num_agents, total_sum_assuared, premium_value, payment_method_CASH, payment_method_CHEQUE
import datetime
features_jan_jun_2019 = []

for i in range (len(data_jan_jun_19)):
  
  temp = policy_jan_jun_19[policy_jan_jun_19['client_code'] == data_jan_jun_19['client_code'][i]]
  temp = temp.sort_values(by=['client_code','policy_snapshot_as_on'], ignore_index = True)

  # policy_term_avg
  policy_term_avg = temp['policy_term']
  policy_term_avg = np.mean(np.array(policy_term_avg))
  #print(policy_term_avg)
  h = 0
  m = 0
  q = 0
  s = 0
  y = 0
  smoke = 0
  spouse_smoke = 0
  cash = 0
  cheque = 0

  inforce_count = temp['status_INFORCE']
  inforce_count = np.sum(np.array(inforce_count))

  lapse_count = temp['status_LAPSED']
  lapse_count = np.sum(np.array(lapse_count))


  terminate_count = 0

  for j in range(len(temp)):
    if temp['Pay_mode_H'][j] == 1:
      h = 1
    if temp['Pay_mode_M'][j] == 1:
      m = 1
    if temp['Pay_mode_Q'][j] == 1:
      q = 1
    if temp['Pay_mode_S'][j] == 1:
      s = 1
    if temp['Pay_mode_Y'][j] == 1:
      y = 1
    if temp['main_smoker_Y'][j] == 1:
      smoke = 1
    if temp['Spouse_smoker_Y'][j] == 1:
      spouse_smoke = 1
    if temp['payment_method_CASH'][j] == 1:
      cash = 1
    if temp['payment_method_CHEQUE'][j] == 1:
      cheque = 1

    if isinstance(temp['termination_dt'][j], datetime.datetime):
      day_ter =  days('2018/12/31', temp['termination_dt'][j])
      day_ter_2 =  days('2019/6/30', temp['termination_dt'][j])
      if day_ter > 0 and day_ter_2 <= 0:
        terminate_count+=1

  if inforce_count == 0:
    lap_inf_ratio = 1
  else:
    lap_inf_ratio = lapse_count/inforce_count

  if inforce_count == 0:
    ter_inf_ratio = 1
  else:
    ter_inf_ratio = terminate_count/inforce_count
  
  num_children = 0

  if isinstance(temp['child1_dob'][len(temp)-1], datetime.datetime) == False:
    num_children +=1
  if isinstance(temp['child2_dob'][len(temp)-1], datetime.datetime) == False:
    num_children +=1
  if isinstance(temp['child3_dob'][len(temp)-1], datetime.datetime) == False:
    num_children +=1
  if isinstance(temp['child4_dob'][len(temp)-1], datetime.datetime) == False:
    num_children +=1
  if isinstance(temp['child5_dob'][len(temp)-1], datetime.datetime) == False:
    num_children +=1
  
  num_policies = temp['policy_code']
  num_policies = num_policies.tolist()
  num_policies = set(num_policies)
  num_policies = len(num_policies)
  
  num_agents = temp['agent_code']
  num_agents = num_agents.tolist()
  num_agents = set(num_agents)
  num_agents = len(num_agents)

  total_sum_assuared_avg = temp['total_sum_assuared']
  total_sum_assuared_avg = np.mean(np.array(total_sum_assuared_avg))
  #print(total_sum_assuared_avg)

  premium_value_avg = temp['premium_value']
  premium_value_avg = np.mean(np.array(premium_value_avg))
  #print(premium_value_avg)

  feat = [policy_term_avg, h, m, q, s, y, smoke, spouse_smoke, inforce_count, lapse_count, terminate_count, lap_inf_ratio, ter_inf_ratio, num_children, num_policies, num_agents, total_sum_assuared_avg, premium_value_avg, cash, cheque]
 # policy_term_avg, Pay_mode_H,	Pay_mode_M,	Pay_mode_Q,	Pay_mode_S,	Pay_mode_Y, main_smoker, spouse_smoker, inforce_count, lapse_count, terminate_count, lap_inf_ratio, ter_inf_ratio, num_children, num_policies, num_agents, total_sum_assuared, premium_value, payment_method_CASH, payment_method_CHEQUE
  
  #print(feat)
  features_jan_jun_2019.append(feat)
  #break

column_names = ['policy_term_avg', 'Pay_mode_H',	'Pay_mode_M',	'Pay_mode_Q',	'Pay_mode_S',	'Pay_mode_Y', 'main_smoker', 'spouse_smoker', 'inforce_count', 'lapse_count', 'terminate_count', 'lap_inf_ratio', 'ter_inf_ratio', 'num_children', 'num_policies', 'num_agents', 'total_sum_assuared', 'premium_value', 'payment_method_CASH', 'payment_method_CHEQUE']
 
features_jan_jun_2019 = pd.DataFrame(features_jan_jun_2019,columns=column_names)



    
print(features_jan_jun_2019.shape)
features_jan_jun_2019.head()

train_data_jan_jun_19 = pd.concat([data_jan_jun_19,features_jan_jun_2019],axis=1)
train_data_jan_jun_19.head()

train_data_jan_jun_19.to_csv('train_data_jan_jun_19.csv',index=False)



# extracting features for july to dec 2019
# policy_term_avg, Pay_mode_H,	Pay_mode_M,	Pay_mode_Q,	Pay_mode_S,	Pay_mode_Y, main_smoker, spouse_smoker, inforce_count, lapse_count, terminate_count, lap_inf_ratio, ter_inf_ratio, num_children, num_policies, num_agents, total_sum_assuared, premium_value, payment_method_CASH, payment_method_CHEQUE
import datetime
features_jul_dec_2019 = []

for i in range (len(data_jul_dec_19)):
  
  temp = policy_jul_dec_19[policy_jul_dec_19['client_code'] == data_jul_dec_19['client_code'][i]]
  temp = temp.sort_values(by=['client_code','policy_snapshot_as_on'], ignore_index = True)

  # policy_term_avg
  policy_term_avg = temp['policy_term']
  policy_term_avg = np.mean(np.array(policy_term_avg))
  #print(policy_term_avg)
  h = 0
  m = 0
  q = 0
  s = 0
  y = 0
  smoke = 0
  spouse_smoke = 0
  cash = 0
  cheque = 0

  inforce_count = temp['status_INFORCE']
  inforce_count = np.sum(np.array(inforce_count))

  lapse_count = temp['status_LAPSED']
  lapse_count = np.sum(np.array(lapse_count))


  terminate_count = 0

  for j in range(len(temp)):
    if temp['Pay_mode_H'][j] == 1:
      h = 1
    if temp['Pay_mode_M'][j] == 1:
      m = 1
    if temp['Pay_mode_Q'][j] == 1:
      q = 1
    if temp['Pay_mode_S'][j] == 1:
      s = 1
    if temp['Pay_mode_Y'][j] == 1:
      y = 1
    if temp['main_smoker_Y'][j] == 1:
      smoke = 1
    if temp['Spouse_smoker_Y'][j] == 1:
      spouse_smoke = 1
    if temp['payment_method_CASH'][j] == 1:
      cash = 1
    if temp['payment_method_CHEQUE'][j] == 1:
      cheque = 1

    if isinstance(temp['termination_dt'][j], datetime.datetime):
      day_ter =  days('2019/06/30', temp['termination_dt'][j])
      day_ter_2 =  days('2019/12/31', temp['termination_dt'][j])
      if day_ter > 0 and day_ter_2 <= 0:
        terminate_count+=1

  if inforce_count == 0:
    lap_inf_ratio = 1
  else:
    lap_inf_ratio = lapse_count/inforce_count

  if inforce_count == 0:
    ter_inf_ratio = 1
  else:
    ter_inf_ratio = terminate_count/inforce_count
  
  num_children = 0

  if isinstance(temp['child1_dob'][len(temp)-1], datetime.datetime) == False:
    num_children +=1
  if isinstance(temp['child2_dob'][len(temp)-1], datetime.datetime) == False:
    num_children +=1
  if isinstance(temp['child3_dob'][len(temp)-1], datetime.datetime) == False:
    num_children +=1
  if isinstance(temp['child4_dob'][len(temp)-1], datetime.datetime) == False:
    num_children +=1
  if isinstance(temp['child5_dob'][len(temp)-1], datetime.datetime) == False:
    num_children +=1
  
  num_policies = temp['policy_code']
  num_policies = num_policies.tolist()
  num_policies = set(num_policies)
  num_policies = len(num_policies)
  
  num_agents = temp['agent_code']
  num_agents = num_agents.tolist()
  num_agents = set(num_agents)
  num_agents = len(num_agents)

  total_sum_assuared_avg = temp['total_sum_assuared']
  total_sum_assuared_avg = np.mean(np.array(total_sum_assuared_avg))
  #print(total_sum_assuared_avg)

  premium_value_avg = temp['premium_value']
  premium_value_avg = np.mean(np.array(premium_value_avg))
  #print(premium_value_avg)

  feat = [policy_term_avg, h, m, q, s, y, smoke, spouse_smoke, inforce_count, lapse_count, terminate_count, lap_inf_ratio, ter_inf_ratio, num_children, num_policies, num_agents, total_sum_assuared_avg, premium_value_avg, cash, cheque]
 # policy_term_avg, Pay_mode_H,	Pay_mode_M,	Pay_mode_Q,	Pay_mode_S,	Pay_mode_Y, main_smoker, spouse_smoker, inforce_count, lapse_count, terminate_count, lap_inf_ratio, ter_inf_ratio, num_children, num_policies, num_agents, total_sum_assuared, premium_value, payment_method_CASH, payment_method_CHEQUE
  
  #print(feat)
  features_jul_dec_2019.append(feat)
  #break

column_names = ['policy_term_avg', 'Pay_mode_H',	'Pay_mode_M',	'Pay_mode_Q',	'Pay_mode_S',	'Pay_mode_Y', 'main_smoker', 'spouse_smoker', 'inforce_count', 'lapse_count', 'terminate_count', 'lap_inf_ratio', 'ter_inf_ratio', 'num_children', 'num_policies', 'num_agents', 'total_sum_assuared', 'premium_value', 'payment_method_CASH', 'payment_method_CHEQUE']
 
features_jul_dec_2019 = pd.DataFrame(features_jul_dec_2019,columns=column_names)



    
print(features_jul_dec_2019.shape)
features_jul_dec_2019.head()

train_data_jul_dec_19 = pd.concat([data_jul_dec_19,features_jul_dec_2019],axis=1)
train_data_jul_dec_19.head()

train_data_jul_dec_19.to_csv('train_data_jul_dec_19.csv',index=False)



# extracting features for jan to jun 2020
# policy_term_avg, Pay_mode_H,	Pay_mode_M,	Pay_mode_Q,	Pay_mode_S,	Pay_mode_Y, main_smoker, spouse_smoker, inforce_count, lapse_count, terminate_count, lap_inf_ratio, ter_inf_ratio, num_children, num_policies, num_agents, total_sum_assuared, premium_value, payment_method_CASH, payment_method_CHEQUE
import datetime
features_jan_jun_2020 = []

for i in range (len(data_jan_jun_20)):
  
  temp = policy_jan_jun_20[policy_jan_jun_20['client_code'] == data_jan_jun_20['client_code'][i]]
  temp = temp.sort_values(by=['client_code','policy_snapshot_as_on'], ignore_index = True)

  # policy_term_avg
  policy_term_avg = temp['policy_term']
  policy_term_avg = np.mean(np.array(policy_term_avg))
  #print(policy_term_avg)
  h = 0
  m = 0
  q = 0
  s = 0
  y = 0
  smoke = 0
  spouse_smoke = 0
  cash = 0
  cheque = 0

  inforce_count = temp['status_INFORCE']
  inforce_count = np.sum(np.array(inforce_count))

  lapse_count = temp['status_LAPSED']
  lapse_count = np.sum(np.array(lapse_count))


  terminate_count = 0

  for j in range(len(temp)):
    if temp['Pay_mode_H'][j] == 1:
      h = 1
    if temp['Pay_mode_M'][j] == 1:
      m = 1
    if temp['Pay_mode_Q'][j] == 1:
      q = 1
    if temp['Pay_mode_S'][j] == 1:
      s = 1
    if temp['Pay_mode_Y'][j] == 1:
      y = 1
    if temp['main_smoker_Y'][j] == 1:
      smoke = 1
    if temp['Spouse_smoker_Y'][j] == 1:
      spouse_smoke = 1
    if temp['payment_method_CASH'][j] == 1:
      cash = 1
    if temp['payment_method_CHEQUE'][j] == 1:
      cheque = 1

    if isinstance(temp['termination_dt'][j], datetime.datetime):
      day_ter =  days('2019/12/31', temp['termination_dt'][j])
      day_ter_2 =  days('2020/6/30', temp['termination_dt'][j])
      if day_ter > 0 and day_ter_2 <= 0:
        terminate_count+=1

  if inforce_count == 0:
    lap_inf_ratio = 1
  else:
    lap_inf_ratio = lapse_count/inforce_count

  if inforce_count == 0:
    ter_inf_ratio = 1
  else:
    ter_inf_ratio = terminate_count/inforce_count
  
  num_children = 0

  if isinstance(temp['child1_dob'][len(temp)-1], datetime.datetime) == False:
    num_children +=1
  if isinstance(temp['child2_dob'][len(temp)-1], datetime.datetime) == False:
    num_children +=1
  if isinstance(temp['child3_dob'][len(temp)-1], datetime.datetime) == False:
    num_children +=1
  if isinstance(temp['child4_dob'][len(temp)-1], datetime.datetime) == False:
    num_children +=1
  if isinstance(temp['child5_dob'][len(temp)-1], datetime.datetime) == False:
    num_children +=1
  
  num_policies = temp['policy_code']
  num_policies = num_policies.tolist()
  num_policies = set(num_policies)
  num_policies = len(num_policies)
  
  num_agents = temp['agent_code']
  num_agents = num_agents.tolist()
  num_agents = set(num_agents)
  num_agents = len(num_agents)

  total_sum_assuared_avg = temp['total_sum_assuared']
  total_sum_assuared_avg = np.mean(np.array(total_sum_assuared_avg))
  #print(total_sum_assuared_avg)

  premium_value_avg = temp['premium_value']
  premium_value_avg = np.mean(np.array(premium_value_avg))
  #print(premium_value_avg)

  feat = [policy_term_avg, h, m, q, s, y, smoke, spouse_smoke, inforce_count, lapse_count, terminate_count, lap_inf_ratio, ter_inf_ratio, num_children, num_policies, num_agents, total_sum_assuared_avg, premium_value_avg, cash, cheque]
 # policy_term_avg, Pay_mode_H,	Pay_mode_M,	Pay_mode_Q,	Pay_mode_S,	Pay_mode_Y, main_smoker, spouse_smoker, inforce_count, lapse_count, terminate_count, lap_inf_ratio, ter_inf_ratio, num_children, num_policies, num_agents, total_sum_assuared, premium_value, payment_method_CASH, payment_method_CHEQUE
  
  #print(feat)
  features_jan_jun_2020.append(feat)
  #break

column_names = ['policy_term_avg', 'Pay_mode_H',	'Pay_mode_M',	'Pay_mode_Q',	'Pay_mode_S',	'Pay_mode_Y', 'main_smoker', 'spouse_smoker', 'inforce_count', 'lapse_count', 'terminate_count', 'lap_inf_ratio', 'ter_inf_ratio', 'num_children', 'num_policies', 'num_agents', 'total_sum_assuared', 'premium_value', 'payment_method_CASH', 'payment_method_CHEQUE']
 
features_jan_jun_2020 = pd.DataFrame(features_jan_jun_2020,columns=column_names)



    
print(features_jan_jun_2020.shape)
features_jan_jun_2020.head()

test_data_jan_jun_20 = pd.concat([data_jan_jun_20,features_jan_jun_2020],axis=1)
test_data_jan_jun_20.head()

test_data_jan_jun_20.head()

test_data_jan_jun_20.to_csv('test_data_jan_jun_20.csv',index=False)

