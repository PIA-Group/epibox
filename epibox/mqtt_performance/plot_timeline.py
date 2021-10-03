# bluit-in
import os

# third-party
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# directory = '/home/ana/Documents/epibox/100rss_test_channels'
directory = '/home/ana/Documents/epibox/1channel_test_rss'

configuration = os.path.basename(directory)

full_df = pd.read_csv(os.path.join(directory, 'df.csv'))

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

plt.figure()
ax = sns.lineplot(
    data=full_df,
    x='timestamp', y='time', hue='file', hue_order=order, alpha=0.5
)
plt.xlabel('time since start [s]')
plt.ylabel('latency [s]')


if 'test_channels' in directory:
    ax.legend(labels=['1 channel', '6 channels', '12 channels'])

elif 'test_rss' in directory:
    ax.legend(labels=['RSS 100%', 'RSS 80%', 'RSS 48%'])

plt.savefig(
    os.path.join(
        directory, 'timeline_{}.png'.format(configuration)
    )
)
# plt.show()

# for label in labels_timestamps:
#     plt.axvline(label[0], color='k')
#     plt.text(label[0], max_latency, 'START', color='k')
#     plt.axvline(label[-1], color='k')
#     plt.text(label[-1], max_latency, 'END', color='k')
