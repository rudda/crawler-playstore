import pandas as pd
import numpy as np

dataframe = pd.read_csv('./data/dataframe.csv', delimiter=",")

print(dataframe.head(2))

dataframe.drop_duplicates(subset ="url",
                     keep = 'first', inplace = True)
df =  dataframe['url']
 
df.to_csv("./data/app_url.csv")


 