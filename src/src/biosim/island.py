import biosim.landscape as ls
from biosim.animals import Herbivore, Carnivore
import random


class Tile:
    """
    A class for each tile/cell on the island
    """
    def __init__(self, landscape, loc, herbs=None, carns=None):
        """
        :param landscape: the landscape of the tile
        :type landscape: class
        :param loc: the location-coordinates of the tile
        :type loc: tuple e.g (3,3)
        :param herbs: the current herbs on the tile
        :type herbs: list
        :param carns: the current carnivores on the tile
        :type carns: list
        """
        self.__loc__ = loc
        if herbs is None:
            self.herbs = []
        else:
            self.herbs = herbs
        if carns is None:
            self.carns = []
        else:
            self.carns = carns
        if landscape.type == "L":
            landscape = ls.Lowland()
        elif landscape.type == "H":
            landscape = ls.Highland()
        elif landscape.type == "D":
            landscape = ls.Desert()
        elif landscape.type == "W":
            landscape = ls.Water()
        else:
            raise ValueError('Invalid landscape')

        self.landscape = landscape
        self.new_h = []
        self.new_c = []
        self.mig_h = []
        self.mig_c = []
        self.traversable = landscape.traversable

    def location(self):
        """
        A function that returns the location of the tile.

        :return : self.__loc__
        :rtype: tuple e.g (2,3)
        """
        return self.__loc__

    def x_coordinates(self):
        """
        A function that returns the x-coordinate of the tile.

        :return: self.__loc__[0]
        :rtype: int
        """
        return self.__loc__[1]

    def y_coordinates(self):
        """
        A function that returns the y-coordinate of the tile.

        :return: self.__loc__[1]
        :rtype: int
        """
        return self.__loc__[0]

    @staticmethod
    def new_location(tile):
        """
        A static method for finding a new tile for migration.

        :param tile: the tile that animals migrate from
        :type tile: Tile class
        :return: new_loc
        :rtype: tuple e.g (2,3)
        """
        r = random.random()
        if r <= 0.25:
            new_loc = (tile.x_coordinates() + 1, tile.y_coordinates())
        elif r <= 0.50:
            new_loc = (tile.x_coordinates() - 1, tile.y_coordinates())
        elif r <= 0.75:
            new_loc = (tile.x_coordinates(), tile.y_coordinates() + 1)
        else:
            new_loc = (tile.x_coordinates(), tile.y_coordinates() - 1)
        return new_loc

    def add_herb_to_tile(self, herbivore):
        """
        A function that adds a herbivore to the current tile.

        :param herbivore: the herbivore that is being added to the tile
        :type herbivore: Herbivore class
        """
        self.herbs.append(herbivore)

    def add_carn_to_tile(self, carnivore):
        """
        A function that adds a carnivore to the current tile.

        :param carnivore: the carnivore that is being added to the tile
        :type carnivore: Carnivore class
        """
        self.carns.append(carnivore)

    def migrants_herbs(self, herb):
        """
        A function that adds a herbivore to a temporary list when it is migrating.

        :param herb: the migrating herbivore
        :type hern: Herbivore class
        """
        self.new_h.append(herb)

    def migrants_carns(self, carn):
        """
        A function that adds a carnivore to a temporary list when it is migrating.

        :param carn:  the migrating carnivore
        :type carn: Carnivore class
        """
        self.new_c.append(carn)

    def integrate(self):
        """
        A class that integrates the migrating animals into the true list containing all
        animals of that species in the current tile. This is done to fix the problem of
        animals migrating twice a year.
        """
        if self.new_h:
            self.herbs += self.new_h
            self.new_h = []
        if self.new_c:
            self.carns += self.new_c
            self.new_c = []

    def feed_herbs(self, fodder):
        """
        A function for "feeding" herbivores in the current tile. The herbivores eat in
        descending order of fitness, until there is no more food to eat.

        :param fodder: total amount of food in the current tile
        :type fodder: int
        """
        if self.herbs:
            self.herbs.sort(key=lambda animal: animal.fitness, reverse=True)
            for herb in self.herbs:
                if fodder > herb.F:
                    herb.eat(herb.F)
                    herb.update_fitness()
                    fodder -= herb.F
                else:
                    herb.eat(fodder)
                    herb.update_fitness()
                    fodder -= fodder

    def feed_carns(self):
        """
        A function for "hunting". The carnivores hunt in a random order, and each carnivore
        hunt until it is full, or has tried to kill every herbivore on the current tile.
        The herbivores are hunted in increasing order of fitness.
        """
        if self.herbs:
            if self.carns:
                random.shuffle(self.carns)
                self.herbs.sort(key=lambda animal: animal.fitness)
                for carn in self.carns:
                    herb_eaten = 0
                    for herb in self.herbs:
                        carn.update_fitness()
                        if carn.fitness < herb.fitness:
                            break
                        if carn.herb_killed(herb.fitness):
                            if herb_eaten < carn.F:
                                herb_eaten += herb.weight
                                carn.eat(herb.weight)
                                carn.update_fitness()
                                herb.dead = True
                                Herbivore.remove_animals()
                            else:
                                carn.eat(carn.F - herb_eaten)
                                carn.update_fitness()
                                herb.dead = True
                                Herbivore.remove_animals()
                                break
                    self.herbs = [herb_survived for herb_survived in self.herbs
                                  if not herb_survived.dead]

    def birth_animal(self):
        """
        A function for calculating the births of the animals on the current tile,
        and adds them to their respective lists.
        """
        if self.herbs:
            breed_herb = len(self.herbs)
            for herb in self.herbs:
                herb.update_fitness()
                j = herb.herb_birth(breed_herb)
                if j is not None:
                    self.herbs.append(j)
        if self.carns:
            breed_carn = len(self.carns)
            for carn in self.carns:
                carn.update_fitness()
                j = carn.carn_birth(breed_carn)
                if j is not None:
                    self.carns.append(j)

    def animals_migrate(self, loc, get_map):
        """
        A function for calculating migration for all animals on the tile. They are added to a
        temporary list in the new tile, and removed from the current tile.

        :param loc: the coordinates of the current tile
        :type loc: tuple e.g (3,3)
        :param get_map: the island map
        :type get_map: a nested list
        """
        for herb in self.herbs:
            herb.update_fitness()
            if herb.migrate():
                new_loc = self.new_location(loc)
                if get_map[new_loc[0] - 1][new_loc[1] - 1].traversable:
                    self.mig_h.append(herb)
                    get_map[new_loc[0] - 1][new_loc[1] - 1].migrants_herbs(herb)
            self.remove_herb()

        for carn in self.carns:
            carn.update_fitness()
            if carn.migrate():
                new_loc = self.new_location(loc)
                if get_map[new_loc[0] - 1][new_loc[1] - 1].traversable:
                    self.mig_c.append(carn)
                    get_map[new_loc[0] - 1][new_loc[1] - 1].migrants_carns(carn)
            self.remove_carn()

    def animals_age(self):
        """
        A function for aging all animals in the current tile
        """
        if self.herbs:
            for herb in self.herbs:
                herb.update_age()

        if self.carns:
            for carn in self.carns:
                carn.update_age()

    def animals_weight_loss(self):
        """
        A function for the weightloss of all animals on the current tile
        """
        if self.herbs:
            for herb in self.herbs:
                herb.losing_weight()

        if self.carns:
            for carn in self.carns:
                carn.losing_weight()

    def animals_dead(self):
        """
        A function that calculates the death of animals on the tile, and removes them from
        their respective lists
        """
        if self.herbs:
            for herb in self.herbs:
                herb.update_fitness()
                herb.death()
            self.herbs = [herb for herb in self.herbs if not herb.dead]
        if self.carns:
            for carn in self.carns:
                carn.update_fitness()
                carn.death()
            self.carns = [carn for carn in self.carns if not carn.dead]

    def remove_herb(self):
        """
        Removes the herbivores that moves to another tile
        """
        if self.mig_h:
            self.herbs = [herb_stay for herb_stay in self.herbs if herb_stay not in self.mig_h]
            self.mig_h = []

    def remove_carn(self):
        """
        Removes the herbivores that moves to another tile
        """
        if self.mig_c:
            self.carns = [carn_stay for carn_stay in self.carns if carn_stay not in self.mig_c]
            self.mig_c = []


class Island:
    """
    Represents the Island for the simulation.
    """
    def __init__(self, geogr):
        """
        :param geogr: a nested lists of landscape-codes
        :type nested lists:
        :raises ValueError: If the map is invalid
        """
        self.map = []
        self.tiles = []
        geogr = geogr.splitlines()
        map_len = len(geogr[0])
        if 'W' in (set(geogr[0]) and set(geogr[len(geogr)-1])) and (len(set(geogr[0])) and
                                                                    len(set(geogr[len(geogr)-1]))) == 1:
            for num, row in enumerate(geogr):
                if len(row) == map_len:
                    section = []
                    if 'W' in row[0] and row[len(row)-1]:
                        for num2, col in enumerate(row):
                            if col == 'W':
                                col = Tile(ls.Water, (num2+1, num+1))
                            elif col == 'L':
                                col = Tile(ls.Lowland, (num2+1, num+1))
                            elif col == 'D':
                                col = Tile(ls.Desert, (num2+1, num+1))
                            elif col == 'H':
                                col = Tile(ls.Highland, (num2+1, num+1))
                            else:
                                raise ValueError('Invalid landscape')
                            section.append(col)
                            self.tiles.append(col)
                        self.map.append(section)
                    else:
                        raise ValueError('Invalid island-map')
                else:
                    raise ValueError('Inconsistent line length')
        else:
            raise ValueError('Invalid island-map')

        self.animals = {'Carnivore': Carnivore,
                        'Herbivore': Herbivore}

    def add_animals(self, population):
        """
        A function that adds animals to the island

        :param population: the animals that are being added to the island
        :type population: list of dicts
        :raises ValueError: If the location is inhabitable

        .. note::
            The list will have to follow the example below:

             [{'loc':(2,2), 'pop':[{'species':'Herbivore', 'age':5,'weight':20},
             {'species':'Carnivore','age':5, 'weight':20}]]

        """
        for animal_type in population:
            get_location = animal_type['loc']
            get_animals = animal_type['pop']
            loc = self.map[get_location[0]-1][get_location[1]-1]
            if loc.traversable:
                for animal in get_animals:
                    if animal['species'] == 'Herbivore':
                        loc.add_herb_to_tile(Herbivore(animal['weight'], animal['age']))
                    elif animal['species'] == 'Carnivore':
                        loc.add_carn_to_tile(Carnivore(animal['weight'], animal['age']))
            else:
                raise ValueError('Inhabitable landscape')

    def yearly_cycle(self):
        """
        A function that runs the annual cycle of the island
        """
        self.feeding()
        self.procreation()
        self.migration()
        self.aging()
        self.loss_of_weight()
        self.death()

    def feeding(self):
        """
        A function that feeds all the animals on the island
        """
        for loc in self.tiles:
            if loc.landscape.food:
                fodder = loc.landscape.f_max
                loc.feed_herbs(fodder)
            loc.feed_carns()

    def procreation(self):
        """
        A function that calculates the births for all animals on the island, and adds them to
        their respective lists
        """
        for loc in self.tiles:
            loc.birth_animal()

    def migration(self):
        """
        A function that calculates migration for all animals on the island, and adds them to their
        respective lists
        """
        for row in self.map:
            for loc in row:
                loc.animals_migrate(loc, self.map)

        for row in self.map:
            for loc in row:
                loc.integrate()

    def aging(self):
        """
        A function that ages all animals on the island
        """
        for loc in self.tiles:
            loc.animals_age()

    def loss_of_weight(self):
        """
        A function that calculate the weight-loss of all the animals on the island
        """
        for loc in self.tiles:
            loc.animals_weight_loss()

    def death(self):
        """
        A function that calculates the deaths of the animals on the island
        """
        for loc in self.tiles:
            loc.animals_dead()
