import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


full_df = pd.read_csv('full_df.csv')

for f in full_df['file'].unique():
    aux = full_df.loc[full_df['file'] == f]

    mean = aux['time'].mean()
    std = aux['time'].std()
    min = aux['time'].min()
    max = aux['time'].max()

    print(f + ':\n')
    print('    {} +/- {} | min: {} | max: {}'.format(mean, std, min, max))

plt.figure()
sns.lineplot(data=full_df, x='timestamp', y='time', hue='file', alpha=0.5)
plt.xlabel('time since start [s]')
plt.ylabel('latency [s]')
plt.legend(['RSSI 100%', 'RSSI 66%'])
plt.show()

""" for label in labels_timestamps:
    plt.axvline(label[0], color='k')
    plt.text(label[0], max_latency, 'START', color='k')
    plt.axvline(label[-1], color='k')
    plt.text(label[-1], max_latency, 'END', color='k') """