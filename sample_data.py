import pandas as pd

df = pd.read_csv("APL_Logistics.csv", encoding='latin1')

df_small = df.sample(min(5000, len(df)))

df_small.to_csv("APL_Logistics_small.csv", index=False)

print("Small file created!")