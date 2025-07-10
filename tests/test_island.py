from src.biosim.island import Island
from src.biosim.animals import Herbivore, Carnivore
import pytest
import textwrap


class TestingIslandTile:
    """
    A class for testing the island and tile class.
    """
    @pytest.fixture(autouse=True)
    def island_map(self):
        """
       Creates an island-map to be used for tests.
        """
        geogr = """\
                WWWWW
                WLLLW
                WHHHW
                WDDDW
                WWWWW
                """
        geogr = textwrap.dedent(geogr)
        self.isla = Island(geogr)
        self.chart = self.isla.map
        herbs = [Herbivore(20, 5) for _ in range(50)]
        carns = [Carnivore(20, 5) for _ in range(50)]
        self.tiles = self.isla.tiles
        self.chart[2][2].herbs = herbs
        self.chart[2][2].carns = carns

    def testing_migration(self, mocker):
        """
        A test where we check if all animals move when random.random gives 0.
        self.chart[2][2] (the center of the chart) should have no animals on it
        (empty list, which is also "False").
        """
        mocker.patch('random.random', return_value=0)
        self.isla.migration()
        assert not (self.chart[2][2].herbs and self.chart[2][2].carns)

    def testing_migration2(self, mocker):
        """
        Here we are testing to see if the merger of new_h and herbs functions correctly
        when random.random is 0, the animal moves to the right.
        """
        mocker.patch('random.random', return_value=0)
        self.isla.migration()
        assert not self.chart[3][2].new_h and self.chart[3][2].herbs

    def testing_tile_loc(self):
        """
        Testing if the loc.location() works as intended.
        """
        loc = self.chart[3][2]
        assert loc.location() == (loc.y_coordinates(), loc.x_coordinates())

    def testing_island_eating(self):
        """
        testing if the island.feeding function works as intended.
        """
        self.chart[2][2].herbs = [Herbivore(20, 5)]
        herbs = self.chart[2][2].herbs
        self.chart[2][2].carns = []
        weight0 = herbs[0].weight
        self.isla.feeding()
        assert weight0 < herbs[0].weight

    def testing_tile_eating2(self, mocker):
        """
        Tests that the carnivores eat all the herbivores when the probabillity is 100%, and that
        the carnivores weight increases.
        """
        mocker.patch('random.random', return_value=0)
        tile = self.chart[2][2]
        tile.herbs = [Herbivore(20, 5)]
        tile.carns = [Carnivore(20, 5)]
        weight0 = tile.carns[0].weight
        tile.carns[0].fitness = 1
        self.isla.feeding()
        assert not tile.herbs and weight0 < tile.carns[0].weight

    def testing_tile_age(self):
        """
        Tests whether the animals age at the expected rate.
        """
        tile = self.chart[2][2]
        age0 = tile.carns[0].age
        self.isla.aging()
        for animal in tile.carns:
            assert age0 + 1 == animal.age

    def testing_tile_dead(self, mocker):
        """
        Check that everybody dies if probof death is 100% (random.random returns 0).
        """
        tile = self.chart[2][2]
        mocker.patch('random.random', return_value=0)
        self.isla.death()
        assert not (tile.herbs or tile.carns)

    def testing_tile_weightloss(self):
        """
        Checks that the weight-loss function works correctly
        """
        tile = self.chart[2][2]
        weight0 = tile.carns[0].weight
        tile.animals_weight_loss()
        for animal in tile.carns:
            assert animal.weight < weight0

    def testing_tile_breeding(self):
        """
        Tests that there are no "dead babies" in the tile.herbs or tile.carns
        """
        tile = self.chart[2][2]
        self.isla.procreation()
        assert None not in (tile.herbs or tile.carns)

    def testing_add_animals1(self):
        """
        testing to see if add_animals works as intended
        """
        tile = self.chart[2][2]
        herbs0 = len(tile.herbs)
        carns0 = len(tile.carns)
        animals = [{'loc': (3, 3),
                    'pop': [{'species': 'Herbivore',
                             'age': 5,
                             'weight': 20},
                            {'species': 'Carnivore',
                             'age': 5,
                             'weight': 20}]}]
        self.isla.add_animals(animals)
        assert (len(tile.herbs) == herbs0 + 1) and (len(tile.carns) == carns0 + 1)


def testing_add_animals2():
    """
    Testing to see if the right error-message is raised when the tile that the animals
    are being added to is inhabitable
    """
    geogr = """\
                   WWWWW
                   WWWWW
                   WWWWW
                   WWWWW
                   WWWWW
                   """
    geogr = textwrap.dedent(geogr)
    isla = Island(geogr)
    with pytest.raises(ValueError):
        isla.add_animals([{'loc': (3, 3),
                           'pop': [{'species': 'Herbivore',
                                    'age': 5,
                                    'weight': 20},
                                   {'species': 'Carnivore',
                                    'age': 5,
                                    'weight': 20}]}])
