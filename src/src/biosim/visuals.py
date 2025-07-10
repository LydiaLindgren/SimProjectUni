import matplotlib.pyplot as plt
import numpy as np
import os
import subprocess


class Visual:
    def __init__(self, island_map, img_step, step, ymax, hist_specs=None, img_name=None,
                 img_dir=None, img_fmt=None, img_base=None, movie_fmt=None):

        self.island_map = island_map
        self.hist_specs = hist_specs
        self.ymax = ymax

        self.step = step
        self.hist_specs = hist_specs
        self.img_step = img_step

        _DEFAULT_GRAPHICS_NAME = 'dv'
        _DEFAULT_MOVIE_FORMAT = 'mp4'
        _DEFAULT_IMG_FORMAT = 'png'
        _FFMPEG_BINARY = 'ffmpeg'
        _MAGICK_BINARY = 'magick'

        if img_name is None:
            self.img_name = _DEFAULT_GRAPHICS_NAME
        else:
            self.img_name = img_name

        self.movie_fmt = movie_fmt

        self.img_dir = img_dir
        self.img_base = img_base

        self.img_fmt = img_fmt if img_fmt is not None else _DEFAULT_IMG_FORMAT

        self.img_ctr = 0
        self.img_step = 1

        self.year = 0

        # Default
        self.fig = None
        self.graph_ax = None
        self.map_ax = None
        self.line1 = None
        self.line2 = None
        self.herbs_col = None
        self.carns_col = None
        self.fitness_hist = None
        self.age_hist = None
        self.weight_hist = None
        self.txt = None

    # This is a modified version of the time_counter.py from inf200-course-materials

    def setup(self, printed_year, num_years):


        if self.fig is None:
            self.fig = plt.figure(figsize=(12,6))#figsize=(12,8)

        self.fig.tight_layout()

        if self.map_ax is None:
            self.map_ax = self.fig.add_subplot(5, 3, (1,4)) #(10,3,(1,10))

        if self.graph_ax is None:
            self.graph_ax = self.fig.add_subplot(5, 3, (3,6)) #(10,3,(3,12))
            self.graph_ax.set_title('Graph Animals')

        self.graph_ax.set_xlim(0, printed_year + num_years + 1)
        self.graph_ax.set_ylim(0, self.ymax)

        self.line1 = self.graph_ax.plot(np.arange(num_years + printed_year + 1),
                                        np.full(num_years + printed_year + 1, np.nan), 'b-')[0]
        self.line2 = self.graph_ax.plot(np.arange(num_years + printed_year + 1),
                                        np.full(num_years + printed_year + 1, np.nan), 'r-')[0]

        if self.herbs_col is None:
            self.herbs_col = self.fig.add_subplot(5, 3, (7,10)) #(10,3,(13,19))
            self.herbs_col.set_title('Herbivore distribution')
            self.herb_axis = None

        if self.carns_col is None:
            self.carns_col = self.fig.add_subplot(5, 3, (9,12)) # (10,3,(15,21))
            self.carns_col.set_title('Carnivore distribution')
            self.carn_axis = None

        if self.hist_specs is None:
            self.hist_specs = {'weight': {'max': 80, 'delta': 2},
                               'fitness': {'max': 1.0, 'delta': 0.05},
                               'age': {'max': 80, 'delta': 2}}

        if self.fitness_hist is None:
            self.fitness_hist = self.fig.add_subplot(5, 3, 13)# (10,3,(22,28)
            self.fitness_hist.set_title('Fitness')
            self.fitness_hist.set_ylim(0, self.ymax)
            fitness_value = self.hist_specs['fitness']
            n_points = int(round(fitness_value['max'] / fitness_value['delta'])) + 1
            self.fitness_lim = np.linspace(0, fitness_value['max'], num=n_points)
            self.fitness_step_herb = self.fitness_hist.step(self.fitness_lim[:-1],
                                                            np.zeros_like(self.fitness_lim[:-1]))[0]
            self.fitness_step_carns = self.fitness_hist.step(self.fitness_lim[:-1],
                                                             np.zeros_like(self.fitness_lim[:-1]))[0]

        if self.age_hist is None:
            self.age_hist = self.fig.add_subplot(5, 3, 14)#(10,3,(23,29))
            self.age_hist.set_title('Age')
            self.age_hist.set_ylim(0, self.ymax)
            age_value = self.hist_specs['age']
            n_points = int(round(age_value['max'] / age_value['delta'])) + 1
            self.age_lim = np.linspace(0, age_value['max'], num=n_points)
            self.age_step_herb = self.age_hist.step(self.age_lim[:-1],
                                                    np.zeros_like(self.age_lim[:-1]))[0]
            self.age_step_carns = self.age_hist.step(self.age_lim[:-1],
                                                     np.zeros_like(self.age_lim[:-1]))[0]

        if self.weight_hist is None:
            self.weight_hist = self.fig.add_subplot(5, 3, 15)#(10,3,(24,30))
            self.weight_hist.set_title('Weight')
            self.weight_hist.set_ylim(0, self.ymax)
            weight_value = self.hist_specs['weight']
            n_points = int(round(weight_value['max'] / weight_value['delta'])) + 1
            self.weight_lim = np.linspace(0, weight_value['max'], num=n_points)
            self.weight_step_herb = self.weight_hist.step(self.weight_lim[:-1],
                                                          np.zeros_like(self.weight_lim[:-1]))[0]
            self.weight_step_carns = self.weight_hist.step(self.weight_lim[:-1],
                                                           np.zeros_like(self.weight_lim[:-1]))[0]


        # axes for text
        if self.txt is None:
            axt = self.fig.add_axes([0.4, 0.8, 0.2, 0.2])  # llx, lly, w, h
            axt.axis('off')  # turn off coordinate system
            self.template = 'year: {:5d}'
            self.txt = axt.text(0.5, 0.5, self.template.format(0),
                                horizontalalignment='center',
                                verticalalignment='center',
                                transform=axt.transAxes)  # relative coordinates

    def update_fitness_hist(self, herbs, carns, ymax):
        counts_herbs = np.histogram(herbs, self.fitness_lim)[0]
        counts_carns = np.histogram(carns, self.fitness_lim)[0]
        if max(counts_carns) > ymax or max(counts_herbs) > ymax:
            ymax = max(max(counts_carns), max(counts_herbs)) * 1.2
            self.fitness_hist.set_ylim(0, ymax)
        self.fitness_step_herb.set_ydata(counts_herbs)
        self.fitness_step_carns.set_ydata(counts_carns)

    def update_age_hist(self, herbs, carns, ymax):
        counts_herbs = np.histogram(herbs, self.age_lim)[0]
        counts_carns = np.histogram(carns, self.age_lim)[0]
        if max(counts_carns) > ymax or max(counts_herbs) > ymax:
            ymax = max(max(counts_carns), max(counts_herbs)) * 1.2
            self.age_hist.set_ylim(0, ymax)
        self.age_step_herb.set_ydata(counts_herbs)
        self.age_step_carns.set_ydata(counts_carns)

    def update_weight_hist(self, herbs, carns, ymax):
        counts_herbs = np.histogram(herbs, self.weight_lim)[0]
        counts_carns = np.histogram(carns, self.weight_lim)[0]
        if max(counts_carns) > ymax or max(counts_herbs) > ymax:
            ymax = max(max(counts_carns), max(counts_herbs)) * 1.2
            self.weight_hist.set_ylim(0, ymax)
        self.weight_step_herb.set_ydata(counts_herbs)
        self.weight_step_carns.set_ydata(counts_carns)

    def update_herb_col(self, sys_map, cmax):
        """
        Updates the 2D-view of the herbivore system.
        """
        if self.herb_axis is not None:
            self.herb_axis.set_data(sys_map)
        else:
            self.herb_axis = self.herbs_col.imshow(sys_map,
                                                   interpolation='nearest',
                                                   vmin=-0, vmax=cmax)
            plt.colorbar(self.herb_axis, ax=self.herbs_col,
                         orientation='vertical')
            self.herbs_col.set_xticks(range(1, len(sys_map[0]), 5))
            self.herbs_col.set_yticks(range(1, len(sys_map), 5))

    def update_carn_col(self, sys_map, cmax):
        """
        Updates the 2D-view of the carnivore system.
        """
        if self.carn_axis is not None:
            self.carn_axis.set_data(sys_map)
        else:
            self.carn_axis = self.carns_col.imshow(sys_map,
                                                   interpolation='nearest',
                                                   vmin=-0, vmax=cmax)

            plt.colorbar(self.carn_axis, ax=self.carns_col,
                         orientation='vertical')
            self.carns_col.set_xticks(range(1, len(sys_map[0]), 5))
            self.carns_col.set_yticks(range(1, len(sys_map), 5))

    # This function is a modified version of the mapping.py file in inf200-course-materials
    def show_map(self):
        #                   R    G    B
        rgb_value = {'W': (0.0, 0.0, 1.0),  # blue
                     'L': (0.0, 0.6, 0.0),  # dark green
                     'H': (0.5, 1.0, 0.5),  # light green
                     'D': (1.0, 1.0, 0.5)}  # light yellow

        map_rgb = [[rgb_value[column] for column in row]
                   for row in self.island_map.splitlines()]

        if self.fig is None:
            self.fig = plt.figure()
            self.map_ax = self.fig.add_subplot(10, 3, (1, 10))

        self.map_ax.imshow(map_rgb)

        self.map_ax.set_xticks(range(0, len(map_rgb[0]), 2))
        self.map_ax.set_xticklabels(range(1, 1 + len(map_rgb[0]), 2))
        self.map_ax.set_yticks(range(0, len(map_rgb), 2))
        self.map_ax.set_yticklabels(range(1, 1 + len(map_rgb), 2))

        self.map_axlg = self.fig.add_axes([0.4, 0.05, 0.05, 0.4])  # llx, lly, w, h
        self.map_axlg.axis('off')

    def update(self, num_years, printed_year, herbs, carns, herb_col, carn_col,
               fit_herb, fit_carns, age_herbs, age_carns, weight_herbs, weight_carns, cmax,
               ymax):
        self.year += 1
        self.show_map()
        self.graph_animals(num_years, herbs, carns, ymax)
        self.txt.set_text(self.template.format(printed_year))
        self.update_herb_col(herb_col, cmax['Herbivores'])
        self.update_carn_col(carn_col, cmax['Carnivores'])
        self.update_fitness_hist(fit_herb, fit_carns, self.ymax)
        self.update_age_hist(age_herbs, age_carns, self.ymax)
        self.update_weight_hist(weight_herbs, weight_carns, self.ymax)
        self.fig.tight_layout()
        self.fig.canvas.flush_events()

        plt.pause(1e-10)

    def graph_animals(self, num_years, herbs, carns, ymax):
        if self.line1 is None:
            self.graph_ax.set_xlim(0, num_years)
            self.graph_ax.set_ylim(0, ymax)

        if self.line1 is None:
            self.line1 = self.graph_ax.plot(np.arange(num_years + 1),
                                            np.full(num_years + 1, np.nan), 'b-')[0]

        if self.line2 is None:
            self.line2 = self.graph_ax.plot(np.arange(num_years+1),
                                            np.full(num_years+1, np.nan), 'r-')[0]

        ydata1 = self.line1.get_ydata()
        ydata2 = self.line2.get_ydata()

        if self.year + 1 == num_years:
            self.save_h = herbs
            self.save_c = carns

        if self.year == num_years:
            ydata1[self.year-1] = self.save_h
            ydata2[self.year-1] = self.save_c
            ydata1[self.year] = herbs
            ydata2[self.year] = carns
        else:
            ydata1[self.year - 1] = herbs
            ydata2[self.year - 1] = carns

        if herbs > ymax or carns > ymax:
            ymax = max(herbs, carns)*1.2
            self.graph_ax.set_ylim(0, ymax)

        self.line1.set_ydata(ydata1)
        self.line2.set_ydata(ydata2)

    def make_movie(self):
        """
             Creates MPEG4 movie from visualization images saved.

             .. :note:
                 Requires ffmpeg for MP4 and magick for GIF

             The movie is stored as img_base + movie_fmt
             """
        _DEFAULT_GRAPHICS_DIR = os.path.join('Results', 'tests')
        _DEFAULT_GRAPHICS_NAME = 'dv'
        _DEFAULT_MOVIE_FORMAT = 'mp4'
        _DEFAULT_IMG_FORMAT = 'png'
        _FFMPEG_BINARY = 'ffmpeg'
        _MAGICK_BINARY = 'magick'

        if self.img_name is None:
            self.img_name = _DEFAULT_GRAPHICS_NAME

        if self.img_dir is not None:
            self.img_base = os.path.join(self.img_dir, self.img_name)
        else:
            self.img_base = None

        self.img_ctr = 0
        self.img_step = 1

        if self.img_base is None:
            raise RuntimeError("No filename defined.")

        if self.movie_fmt is None:
            self.movie_fmt = _DEFAULT_MOVIE_FORMAT

        if self.movie_fmt == 'mp4':
            try:
                # Parameters chosen according to http://trac.ffmpeg.org/wiki/Encode/H.264,
                # section "Compatibility"
                subprocess.check_call([_FFMPEG_BINARY,
                                       '-i', '{}_%05d.png'.format(self.img_base),
                                       '-y',
                                       '-profile:v', 'baseline',
                                       '-level', '3.0',
                                       '-pix_fmt', 'yuv420p',
                                       '{}.{}'.format(self.img_base, self.movie_fmt)])
            except subprocess.CalledProcessError as err:
                raise RuntimeError('ERROR: ffmpeg failed with: {}'.format(err))
        elif self.movie_fmt == 'gif':
            try:
                subprocess.check_call([_MAGICK_BINARY,
                                       '-delay', '1',
                                       '-loop', '0',
                                       '{}_*.png'.format(self.img_base),
                                       '{}.{}'.format(self.img_base, self.movie_fmt)])
            except subprocess.CalledProcessError as err:
                raise RuntimeError('ERROR: convert failed with: {}'.format(err))
        else:
            raise ValueError('Unknown movie format: ' + self.movie_fmt)

        if self.img_base is None or self.step % self.img_step != 0:
            return

    def save_plot(self):
        if self.img_base is not None:
            plt.savefig(os.path.join(self.img_dir, f'{self.img_base}_{self.img_ctr:05d}.'
                                                   f'{self.img_fmt}'))
            self.img_ctr += 1
