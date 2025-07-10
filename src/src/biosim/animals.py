import math
import random


class Animal:
    """A class with the common traits of Herbivores and Carnivores"""
    def update_fitness(self):
        r"""
        A function that updates the fitness of an animal. It is called before it is
        used in calculations


        .. math::

            q^±(x, x{\frac{1}{2}}, \phi) = \frac {1} {1 + e^{±\phi \times (x - x{\frac{1}{2}})}}



        :math:`\phi = 0` if :math:`w \leq 0`

        :math:`\phi = q^+ *q^-` otherwise

        formula above

        """
        if self.fitness_update:
            self.fitness = 0 if self.weight <= 0 \
                else (1 / (1 + math.exp(self.phi_age * (self.age - self.a_half)))) * \
                     (1 / (1 + math.exp(-self.phi_weight * (self.weight - self.w_half))))
            self.fitness_update = False

    def losing_weight(self):
        """
        A function that updates the weight of an animal.
        """
        self.weight -= self.eta * self.weight
        self.fitness_update = True

    def update_age(self):
        """
        A function that updates the age of an animal.
        """
        self.age += 1
        self.fitness_update = True

    def migrate(self):
        """
        A function that tells if an animal is going to migrate any given years

        :return: bool
        :rtype: True or False
        """
        if self.mu * self.fitness >= random.random():
            return True
        else:
            return False

    def eat(self, amount):
        """
        Updates the weight of the animal

        :param amount: The amount of food being eaten
        :type amount: int

        """
        self.weight += self.beta * amount
        self.fitness_update = True


# noinspection PyPep8Naming
class Herbivore(Animal):
    """
    A class for the Herbivore-species. They will act as the food-source for the Carnivores,
    and will act according to their parameters and specifications.
    """
    a_half = 40
    w_half = 10
    phi_age = 0.6
    phi_weight = 0.1
    beta = 0.9
    eta = 0.05
    gamma = 0.2
    zeta = 3.5
    xi = 1.2
    omega = 0.4
    w_birth = 8
    sigma_birth = 1.5
    F = 10
    mu = 0.25

    default_params = {'a_half': a_half,
                      'w_half': w_half,
                      'phi_age': phi_age,
                      'phi_weight': phi_weight,
                      'beta': beta,
                      'eta': eta,
                      'gamma': gamma,
                      'zeta': zeta,
                      'xi': xi,
                      'omega': omega,
                      'w_birth': w_birth,
                      'sigma_birth': sigma_birth,
                      'F': F,
                      'mu': mu}

    instance_count = 0

    @classmethod
    def count_animals(cls):
        """
        A class method that updates the number of instances of the Herbivore species.
        The instance_count is used to track the number of animals currently on the
        island. It is called at "birth" or at the creation of an animal.
        """
        cls.instance_count += 1

    @classmethod
    def remove_animals(cls):
        """
        A class method that updates the number of instances of Herbivore.
        The instance_count is used to track the number of animals currently on the
        Island. It is called at the death of an animal.
        """
        cls.instance_count -= 1

    @classmethod
    def set_params(cls, new_params):
        """
        :param new_params: dict of new parameters e.g {param:value}
        :type dict: {str:float}
        :raise KeyError:
        """
        for key in new_params:
            if key not in ('beta', 'eta', 'a_half', 'phi_age', 'w_half', 'phi_weight', 'mu',
                           'gamma', 'zeta', 'xi', 'omega', 'w_birth', 'F', 'sigma_birth','mu'):
                raise KeyError('Invalid parameter name: ' + key)

        if 'beta' in new_params:
            cls.beta = new_params['beta']
        if 'a_half' in new_params:
            cls.a_half = new_params['a_half']
        if 'phi_age' in new_params:
            cls.phi_age = new_params['phi_age']
        if 'w_half' in new_params:
            cls.w_half = new_params['w_half']
        if 'phi_weight' in new_params:
            cls.phi_weight = new_params['phi_weight']
        if 'mu' in new_params:
            cls.mu = new_params['mu']
        if 'gamma' in new_params:
            cls.gamma = new_params['gamma']
        if 'zeta' in new_params:
            cls.zeta = new_params['zeta']
        if 'xi' in new_params:
            cls.xi = new_params['xi']
        if 'omega' in new_params:
            cls.omega = new_params['omega']
        if 'w_birth' in new_params:
            cls.w_birth = new_params['w_birth']
        if 'sigma_birth' in new_params:
            cls.sigma_birth = new_params['sigma_birth']
        if 'F' in new_params:
            cls.F = new_params['F']
        if 'mu' in new_params:
            cls.mu = new_params['mu']

    @classmethod
    def disp_herbs(cls):
        """
        A classmethod that prints the current number of Herbivores on the island
        """
        print('number of herbivores:', cls.instance_count)

    def __init__(self, weight, age):
        """
        :param weight: weight of the animal
        :type weight: int
        :param age: age of the animal (0 at birth)
        :type age: int
        """
        self.count_animals()
        self.dead = False
        self.weight = weight
        self.age = age
        self.fitness = 0 if self.weight <= 0 else \
            (1 / (1 + math.exp(self.phi_age * (self.age - self.a_half)))) * \
            (1 / (1 + math.exp(-self.phi_weight * (self.weight - self.w_half))))
        self.fitness_update = False

    def herb_birth(self, num_herb):
        """
        A function for herbivores giving birth
        :param num_herb: number of herbivores in a tile/cell

        :return: Herbivore or None
        """
        self.prob = 0 if self.weight < self.zeta * (self.w_birth + self.sigma_birth)\
            else min(1, self.gamma * self.fitness * (num_herb - 1))
        if self.prob > random.random():
            new_weight = random.gauss(self.w_birth, self.sigma_birth)
            if new_weight > 0:
                self.weight -= self.xi * new_weight
                self.fitness_update = True
                return Herbivore(new_weight, 0)

    def death(self):
        """
        A function for calculating if a herbivore dies

        :return self.dead:
        :rtype: True or False
        """
        if self.weight <= 0 or random.random() < self.omega * (1 - self.fitness):
            self.dead = True
            self.remove_animals()
        return self.dead


class Carnivore(Animal):
    """
    A class for the Carnivore-species. They will act as the hunter on the island,
    and will act according to their parameters and specifications. It will only eat Herbivores
    """
    beta = 0.75
    eta = 0.125
    a_half = 40
    phi_age = 0.3
    w_half = 4
    phi_weight = 0.4
    mu = 0.4
    gamma = 0.8
    zeta = 3.5
    xi = 1.1
    omega = 0.8
    w_birth = 6
    sigma_birth = 1
    F = 50
    DeltaPhiMax = 10

    default_params = {'beta': beta,
                      'eta': eta,
                      'a_half': a_half,
                      'phi_age': phi_age,
                      'w_half': w_half,
                      'phi_weight': phi_weight,
                      'mu': mu,
                      'gamma': gamma,
                      'zeta': zeta,
                      'xi': xi,
                      'omega': omega,
                      'F': F,
                      'DeltaPhiMax': DeltaPhiMax,
                      'sigma_birth': sigma_birth,
                      'w_birth': w_birth}

    instance_count = 0

    @classmethod
    def set_params(cls, new_params):
        """
        A class method that updates the number of instances of the Carnivore species.
        The instance_count is used to track the number of animals currently on the
        island. It is called at "birth" or at the creation of an animal.
        """
        for key in new_params:
            if key not in ('beta', 'eta', 'a_half', 'phi_age', 'w_half', 'phi_weight', 'mu',
                           'gamma', 'zeta', 'xi', 'omega', 'F', 'DeltaPhiMax', 'sigma_birth',
                           'w_birth'):
                raise KeyError('Invalid parameter name: ' + key)

        if 'beta' in new_params:
            cls.beta = new_params['beta']
        if 'a_half' in new_params:
            cls.a_half = new_params['a_half']
        if 'phi_age' in new_params:
            cls.phi_age = new_params['phi_age']
        if 'w_half' in new_params:
            cls.w_half = new_params['w_half']
        if 'phi_weight' in new_params:
            cls.phi_weight = new_params['phi_weight']
        if 'mu' in new_params:
            cls.mu = new_params['mu']
        if 'gamma' in new_params:
            cls.gamma = new_params['gamma']
        if 'zeta' in new_params:
            cls.zeta = new_params['zeta']
        if 'xi' in new_params:
            cls.xi = new_params['xi']
        if 'omega' in new_params:
            cls.omega = new_params['omega']
        if 'w_birth' in new_params:
            cls.w_birth = new_params['w_birth']
        if 'sigma_birth' in new_params:
            cls.sigma_birth = new_params['sigma_birth']
        if 'F' in new_params:
            cls.F = new_params['F']
        if 'DeltaPhiMax' in new_params:
            cls.DeltaPhiMax = new_params['DeltaPhiMax']

    @classmethod
    def disp_carns(cls):
        """
        A function for printing the number of carnivores on the island.
        """
        print('number of herbivores:', cls.instance_count)

    @classmethod
    def count_animals(cls):
        """A class method that updates the number of instances of a species (Herbivore or
           Carnivore). The instance_count is used to track the number of animals currently in
           "existence". It is called at "birth" or at the creation of an animal."""
        cls.instance_count += 1

    @classmethod
    def remove_animals(cls):
        """A class method that updates the number of instances of a species (Herbivore or
        Carnivore). The instance_count is used to track the number of animals currently in
        "existence". It is called at the "death" of an animal."""
        cls.instance_count -= 1

    def __init__(self, weight, age):
        """
        :param weight: weight of the animal
        :type weight: int
        :param age: age of the animal (0 at birth)
        :type age: int
        """
        self.count_animals()
        self.dead = False
        self.weight = weight
        self.age = age
        self.fitness = 0 if self.weight <= 0 else 1 / (1 + math.exp(self.phi_age * (self.age - self.a_half))) * \
                                                  1 / (1 + math.exp(-self.phi_weight * (self.weight - self.w_half)))
        self.fitness_update = False

    def herb_killed(self, herb_fitness):
        """
        A funtction that calculates whether or not a Carnivore will kill (and later eat)
        a Herbivore.

        :param herb_fitness: the fitness of the Herbivore in question
        :return: bool
        :rtype: True or False
        """
        if self.fitness <= herb_fitness:
            return False
        elif (self.fitness > herb_fitness) and ((self.fitness - herb_fitness) < self.DeltaPhiMax):
            if ((self.fitness - herb_fitness) / self.DeltaPhiMax) > random.random():
                return True
            else:
                return False
        else:
            return True

    def carn_birth(self, num_carn):
        """
        A function for the Carnivore giving birth.

        :param num_carn: The number of varnivores in a cell/tile
        :return: Carnivore or None
        """
        self.prob = 0 if self.weight < self.zeta * (self.w_birth + self.sigma_birth) \
            else min(1, self.gamma * self.fitness * (num_carn - 1))
        r = random.random()
        if r < self.prob:
            new_weight = random.gauss(self.w_birth, self.sigma_birth)
            if new_weight > 0:
                self.weight -= self.xi * new_weight
                self.fitness_update = True
                return Carnivore(new_weight, 0)

    def death(self):
        """
        A function that calculates whether a Carnivore dies or not.

        :returns: self.dead
        :rtype: True or False
       """
        if self.weight <= 0 or random.random() < self.omega * (1 - self.fitness):
            self.dead = True
            self.remove_animals()
        return self.dead
