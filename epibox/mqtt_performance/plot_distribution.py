# built-in
import os

# third-party
# import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.cbook import boxplot_stats


directory = '/home/ana/Documents/epibox/100rss_test_channels'
# directory = '/home/ana/Documents/epibox/12channels_test_rss'
configuration = os.path.basename(directory)

# median_file = open(
#     '/home/ana/Documents/epibox/median_latency_{}.txt'.format(
#         configuration.split('_')[0]
#     ),
#     'w'
# )

full_df = pd.read_csv(os.path.join(directory, 'df.csv'))

for f in full_df['file'].unique():
    aux = full_df.loc[full_df['file'] == f]

    mean = aux['time'].mean()
    median = aux['time'].median()
    std = aux['time'].std()

    # np.savetxt(
    #     median_file,
    #     [[f, median]],
    #     fmt='%s: %s'
    # )

    print(f + ':\n')
    print(
        '    {} | {} +/- {}'.format(
            median, mean, std
        )
    )
    print('    # messages: {}'.format(len(aux)))

if 'test_channels' in directory:
    order = (
        [
            '1channel_{}.txt'.format(configuration.split('_')[0]),
            '6channels_{}.txt'.format(configuration.split('_')[0]),
            '12channels_{}.txt'.format(configuration.split('_')[0]),
        ]
    )

elif 'test_rss' in directory:
    order = (
        [
            '{}_100rss.txt'.format(configuration.split('_')[0]),
            '{}_80rss.txt'.format(configuration.split('_')[0]),
            '{}_48rss.txt'.format(configuration.split('_')[0]),
        ]
    )

print(order)

plt.figure()
ax = sns.boxplot(data=full_df, x='file', y='time', order=order)
# sns.lineplot(data=full_df, x='timestamp', y='time', hue='file', alpha=0.5)
# sns.histplot(data=full_df, x="time", hue="file", bins=100)
plt.ylabel('latency [s]')

labels = ax.get_xticklabels()
if 'test_channels' in directory:
    ax.set_xticklabels(['1 channel', '6 channels', '12 channels'])
    plt.xlabel('# of channels')

elif 'test_rss' in directory:
    ax.set_xticklabels(['100%', '80%', '48%'])
    plt.xlabel('RSS')

plt.savefig(
    os.path.join(
        directory, 'boxplot_{}.png'.format(configuration)
    )
)

whislo = 0
whishi = 0
for conf in order:
    stats = boxplot_stats(
        full_df.loc[full_df['file'] == conf]['time']
    )
    whislo = min([whislo, stats[0]['whislo']])
    whishi = max([whishi, stats[0]['whishi']])

plt.ylim((whislo, whishi+0.0001))

plt.savefig(
    os.path.join(
        directory, 'boxplot_zoom_{}.png'.format(configuration)
    )
)

# plt.show()

outliers = [y for stat in stats for y in stat['fliers']]

print('ratio of outliers: {}'.format(len(outliers)/len(full_df)))

print('done')
