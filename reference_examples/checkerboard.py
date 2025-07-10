__author__ = 'Hans Ekkehard Plesser, NMBU'
"""
A simulation showing the migrations of herbivores if they move once every year. This script is mainly for visualization 
purposes
"""

import textwrap
from biosim.simulation import BioSim

if __name__ == '__main__':

    geogr = """\
               WWWWWWWWWWWWWWWWWWWWWWW
               WDDDDDDDDDDDDDDDDDDDDDW
               WDDDDDDDDDDDDDDDDDDDDDW
               WDDDDDDDDDDDDDDDDDDDDDW
               WDDDDDDDDDDDDDDDDDDDDDW
               WDDDDDDDDDDDDDDDDDDDDDW
               WDDDDDDDDDDDDDDDDDDDDDW
               WDDDDDDDDDDDDDDDDDDDDDW
               WDDDDDDDDDDDDDDDDDDDDDW
               WDDDDDDDDDDDDDDDDDDDDDW
               WDDDDDDDDDDDDDDDDDDDDDW
               WDDDDDDDDDDDDDDDDDDDDDW
               WDDDDDDDDDDDDDDDDDDDDDW
               WDDDDDDDDDDDDDDDDDDDDDW
               WDDDDDDDDDDDDDDDDDDDDDW
               WDDDDDDDDDDDDDDDDDDDDDW
               WDDDDDDDDDDDDDDDDDDDDDW
               WWWWWWWWWWWWWWWWWWWWWWW
               """
    geogr = textwrap.dedent(geogr)

    ini_herbs = [{'loc': (9,12),
                  'pop': [{'species': 'Herbivore',
                           'age': 5,
                           'weight': 20}
                          for _ in range(20000)]}]


    sim = BioSim(geogr, ini_herbs, seed=1,
                 hist_specs={'fitness': {'max': 1.0, 'delta': 0.05},
                             'age': {'max': 60.0, 'delta': 2},
                             'weight': {'max': 60, 'delta': 2}},
                 cmax_animals={'Herbivores': 10, 'Carnivores': 50},
                 img_dir='results',
                 img_base='checkerboard')
    sim.set_animal_parameters('Herbivore',{'mu':100})
    sim.simulate(30)
    sim.make_movie()

    input('Press ENTER')