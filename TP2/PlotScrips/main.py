from utils import read_spice_data, read_json_data
import matplotlib.pyplot as plt
from matplotlib.ticker import EngFormatter

if __name__ == '__main__':
    plots = read_json_data('plot_info.json')['plots']
    for plot in plots:
        filename = plot['spice_filename']
        data_filename = 'resources/' + filename + '.txt'
        data = read_spice_data(data_filename)
        time = data[plot['spice_time_label']]

        plt.title(plot['title'])

        fig, ax1 = plt.subplots()
        fig.set_size_inches(14, 8)

        # left y axis
        ax1.set_ylabel(plot['left_y_label'])
        ax1.set_xlabel(plot['x_label'])
        ax1.set_ylim(tuple(plot['left_y_limit']))

        formatter1 = EngFormatter(places=2, sep="\N{THIN SPACE}")  # U+2009
        plt.gca().xaxis.set_major_formatter(formatter1)

        ax1.set_xlim(tuple(plot['x_limit']))

        plt.grid(True)
        if not plot['is_one_direction']:
            ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
            ax2.set_ylabel(plot['right_y_label'])  # we already handled the x-label with ax1
            ax2.set_ylim(tuple(plot['right_y_limit']))

        lines = []
        labels = []
        for graphic in plot['graphics']:
            curr_data = data[graphic['spice_label']]
            if plot['is_one_direction']:
                line = ax1.plot(time, curr_data, label=graphic['label'], linestyle=graphic['linestyle'], color=graphic['color'])[0]
                label = line.get_label()
            else:
                if not graphic['belongsToRightYAxis']:
                    line = ax1.plot(time, curr_data, label=graphic['label'], linestyle=graphic['linestyle'], color=graphic['color'])[0]
                    label = line.get_label()
                else:
                    line = ax2.plot(time, curr_data, label=graphic['label'], linestyle=graphic['linestyle'], color=graphic['color'])[0]
                    label = line.get_label()
            lines.append(line)
            labels.append(label)

        plt.legend(lines, labels)
        plt.savefig('output/' + plot['title'])
