# built-in
import os

# third-party
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

directory = '/home/ana/Documents/epibox'

full_df = pd.DataFrame(columns=['timestamp', 'time', 'key', 'file'])
labels_timestamps = []

for run_file in [f for f in os.listdir(directory) if 'run' in f]:

    # startup_time = startup_file.split('_')[-1]
    # run_file = 'mqtt_timestamps_run_' + startup_time
    
    startup_time = run_file.split('_')[-1]

    file_path = os.path.join(directory, run_file)
    df = pd.read_csv(file_path, sep=', ', header=None, names=['timestamp', 'id', 'key'])

    # file_path = os.path.join(directory, run_file)
    # df_aux = pd.read_csv(file_path, sep=', ', header=None, names=['timestamp', 'id', 'key'])
    # df = df.append(df_aux, ignore_index=True)

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
        print(times)

    times['timestamp'] = times['timestamp'] - times.iloc[0]['timestamp']
    times['file'] = startup_time

    full_df = full_df.append(times, ignore_index=True)

    data_group = times.loc[times['key'] == 'DATA']
    labels_timestamps += [[data_group.iloc[0]['timestamp'], data_group.iloc[-1]['timestamp']]]
    
full_df.to_csv('df_76rss.csv')
