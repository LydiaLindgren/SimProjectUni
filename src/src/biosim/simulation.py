"""
Template for BioSim class.
"""

# The material in this file is licensed under the BSD 3-clause license
# https://opensource.org/licenses/BSD-3-Clause
# (C) Copyright 2021 Hans Ekkehard Plesser / NMBU

from biosim.island import Island
from biosim.landscape import Lowland, Highland, Water, Desert
from biosim.animals import Herbivore, Carnivore
from biosim.visuals import Visual
import random
import csv
import matplotlib
matplotlib.use("TkAgg")


class BioSim:
    """
    Simulates a BioSim project.
    """
    def __init__(self, island_map, ini_pop, seed,
                 vis_years=1, ymax_animals=None, cmax_animals=None, hist_specs=None,
                 img_dir=None, img_base=None, img_fmt='png', img_years=None,
                 log_file=None):
        """
        :param island_map: Multi-line string specifying island geography
        :param ini_pop: List of dictionaries specifying initial population
        :param seed: Integer used as random number seed
        :param ymax_animals: Number specifying y-axis limit for graph showing animal numbers
        :param cmax_animals: Dict specifying color-code limits for animal densities
        :param hist_specs: Specifications for histograms, see below
        :param vis_years: years between visualization updates (if 0, disable graphics)
        :param img_dir: String with path to directory for figures
        :param img_base: String with beginning of file name for figures
        :param img_fmt: String with file type for figures, e.g. 'png'
        :param img_years: years between visualizations saved to files (default: vis_years)
        :param log_file: If given, write animal counts to this file

        If ymax_animals is None, the y-axis limit should be adjusted automatically.
        If cmax_animals is None, fixed default values should be used.
         cmax_animals is a dict mapping species names to numbers, e.g.,
           {'Herbivore': 50, 'Carnivore': 20}

        hist_specs is a dictionary with one entry per property for which a histogram shall be shown.
        For each property, a dictionary providing the maximum value and the bin width must be given.

        If img_dir is None, no figures are written to file. Filenames are formed as
            f'{os.path.join(img_dir, img_base}_{img_number:05d}.{img_fmt}'
        where img_number are consecutive image numbers starting from 0.

        img_dir and img_base must either be both None or both strings.
        """
        random.seed(seed)
        Carnivore.instance_count = 0
        Herbivore.instance_count = 0
        self.vis_years = vis_years

        if ymax_animals is None:
            self.ymax_animals = 5000
        else:
            self.ymax_animals = ymax_animals

        if cmax_animals is None:
            self.cmax_animals = {'Herbivores': 150,
                                 'Carnivores': 80}
        else:
            self.cmax_animals = cmax_animals

        if self.vis_years != 0:
            self.graphics = Visual(island_map, img_years, vis_years, ymax=self.ymax_animals,
                                   img_dir=img_dir, img_name=img_base,
                                   img_fmt=img_fmt, img_base=img_base, hist_specs=hist_specs)
            self.vis_years = vis_years
            self.img_dir = img_dir
            self.img_base = img_base
            self.img_fmt = img_fmt

            if img_years is None:
                self.img_years = vis_years
            else:
                self.img_years = img_years

        self.log_file = log_file
        if self.log_file is not None:
            with open(f'Results/{log_file}', 'w') as f:
                writer = csv.writer(f)
                writer.writerow(['Year', 'Herbivores', 'Carnivores'])

        self.island = Island(island_map)
        self.tiles = self.island.tiles

        self.add_population(ini_pop)
        self.current_year = 0

    @staticmethod
    def set_animal_parameters(species, params):
        """
        Sets parameters for animal species.
        """
        if species == 'Herbivore':
            Herbivore.set_params(params)
        elif species == 'Carnivore':
            Carnivore.set_params(params)
        else:
            print('Wrong species or species names')

    @staticmethod
    def set_landscape_parameters(landscape, params):
        """
        Sets parameters for landscape type.
        """
        if landscape == 'L':
            Lowland.set_params(params)
        elif landscape == 'H':
            Highland.set_params(params)
        elif landscape == 'W':
            Water.set_params(params)
        elif landscape == 'D':
            Desert.set_params(params)
        else:
            print('Landscape type not recognized.')

    def simulate(self, num_years):
        """
        Runs simulation while visualizing the result.
        """
        if self.vis_years != 0:
            self.graphics.setup(self.current_year, num_years)

        for year in range(num_years):
            self.current_year += 1
            herb_col = []
            carn_col = []

            herb_age = []
            carn_age = []
            herb_fitness = []
            carn_fitness = []
            herb_weight = []
            carn_weight = []
            for tile in self.island.tiles:
                herb_age += [ani.age for ani in tile.herbs]
                carn_age += [ani.age for ani in tile.carns]
                herb_fitness += [ani.fitness for ani in tile.herbs]
                carn_fitness += [ani.fitness for ani in tile.carns]
                herb_weight += [ani.weight for ani in tile.herbs]
                carn_weight += [ani.weight for ani in tile.carns]

            for row in self.island.map:
                herb_ins = []
                carn_ins = []
                for an in row:
                    herb_ins.append(len(an.herbs))
                    carn_ins.append(len(an.carns))
                herb_col.append(herb_ins)
                carn_col.append(carn_ins)

            if self.vis_years != 0:
                if self.current_year % self.vis_years == 0:
                    self.graphics.update(num_years=num_years, printed_year=self.current_year,
                                         herbs=Herbivore.instance_count, carns=Carnivore.instance_count,
                                         herb_col=herb_col, carn_col=carn_col,
                                         fit_herb=herb_fitness, fit_carns=carn_fitness,
                                         age_herbs=herb_age, age_carns=carn_age,
                                         weight_herbs=herb_weight, weight_carns=carn_weight, cmax=self.cmax_animals,
                                         ymax=self.ymax_animals)

            self.island.yearly_cycle()

            if self.vis_years != 0:
                if self.current_year % self.img_years == 0:
                    self.graphics.save_plot()

            if self.log_file is not None:
                with open(f'Results/{self.log_file}', 'a') as f:
                    writer = csv.writer(f)
                    writer.writerow([self.current_year, Herbivore.instance_count,
                                     Carnivore.instance_count])

    def add_population(self, population):
        """
        Adds a population to the island.
        """
        self.island.add_animals(population)

    @property
    def year(self):
        """
        Last year simulated.
        """
        return self.current_year

    @property
    def num_animals(self):
        """Total number of animals on island."""
        return Carnivore.instance_count + Herbivore.instance_count

    @property
    def num_animals_per_species(self):
        """Number of animals per species in island, as dictionary."""
        num_herbs = Herbivore.instance_count
        num_carns = Carnivore.instance_count
        ani_per_species = {'Herbivore': num_herbs,
                           'Carnivore': num_carns}
        return ani_per_species

    def make_movie(self):
        """Create MPEG4 movie from visualization images saved."""
        self.graphics.make_movie()
