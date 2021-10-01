# built-in
import os

# third-party
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


full_df = pd.read_csv('df_76rss.csv')
    
plt.figure()
#sns.lineplot(data=full_df, x='timestamp', y='time', hue='file', alpha=0.5)
sns.histplot(data=full_df, x="timestamp", hue="file", alpha=0.5)
plt.xlabel('time since start [s]')
plt.ylabel('latency [s]')
plt.show()

print('done')