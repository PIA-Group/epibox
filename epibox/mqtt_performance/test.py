# built-in
import os

# third-party
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

directory = '/home/ana/Documents/epibox'
startup_file = 'mqtt_timestamps_startup_2021-09-22 11-55-27.txt'
time = startup_file.split('_')[-1]
run_file = 'mqtt_timestamps_startup_' + time

file_path = os.path.join(directory, startup_file)
df = pd.read_csv(file_path, sep=', ', header=None, names=['timestamp', 'id', 'key'])

file_path = os.path.join(directory, run_file)
df_aux = pd.read_csv(file_path, sep=', ', header=None, names=['timestamp', 'id', 'key'])
df = df.append(df_aux, ignore_index=True)

ids = df['id'].unique()

times = pd.DataFrame([], columns=['timestamp', 'time', 'key'])

for id in ids:
    a = df.loc[df['id'] == id]
    try:
        result = a.iloc[1]['timestamp'] - a.iloc[0]['timestamp']
        print(result)

    except Exception as e:
        print('{} -- {}'.format(e, a))

    times = times.append(pd.DataFrame([[a.iloc[0,0], result, a.iloc[0,2]]], columns=['timestamp', 'time', 'key']), ignore_index=True)
    print(times.iloc[0]['timestamp'])
    #times['timestamp'] = times['timestamp'] - times.iloc[0]['timestamp']
    print(times)

times['timestamp'] = times['timestamp'] - times.iloc[0]['timestamp']
data_group = times.loc[times['key'] == 'DATA']

max_latency = times['time'].max()

    
plt.figure()
sns.lineplot(data=times, x='timestamp', y='time')
plt.axvline(data_group.iloc[0]['timestamp'], color='tab:orange')
plt.text(data_group.iloc[0]['timestamp'], max_latency, 'START', color='tab:orange')
plt.axvline(data_group.iloc[-1]['timestamp'], color='tab:orange')
plt.text(data_group.iloc[-1]['timestamp'], max_latency, 'END', color='tab:orange')
plt.xlabel('time since start [s]')
plt.ylabel('latency [s]')
plt.show()



print('done')