import pytest
from biosim.animals import Herbivore, Carnivore
"""
This file tests various aspects of the animal class
"""


@pytest.fixture(autouse=True)
def reset_params():
    """
    Resets the parameters after every test
    """
    yield
    Herbivore.set_params(Herbivore.default_params)


@pytest.mark.parametrize('class_to_test', [Herbivore, Carnivore])
def test_params(class_to_test):
    """
    Checking if the parameters update as it should
    """
    ani = class_to_test(20, 5)
    sigma0 = ani.sigma_birth
    new_params = {'sigma_birth': 10}
    ani.set_params(new_params)
    assert sigma0 != ani.sigma_birth


@pytest.mark.parametrize('class_to_test', [Herbivore, Carnivore])
def test_migrate(class_to_test, mocker):
    """
    Checking that an animal will move if the probability is 100%.
    Mocker.patch ensure this
    """
    mocker.patch('random.random', return_value=0)
    ani = class_to_test(20, 5)
    assert ani.migrate()


class Test_herbivore:
    """
    A class for testing the Herbivore-class.
    """
    @pytest.fixture(autouse=True)
    def herb(self):
        """
        Making a Herbivore that will be used for further tests.
        """
        weight0 = 10
        age0 = 5
        self.ani = Herbivore(weight0, age0)

    @pytest.fixture(autouse=True)
    def reset_params(self):
        """
        resets parameters after every tests
        """
        yield
        Herbivore.set_params(Herbivore.default_params)

    def test_eating(self):
        """
        Test that the herbivores weight updates as it should
        """
        weight0 = self.ani.weight
        self.ani.eat(self.ani.F)
        assert self.ani.weight == self.ani.beta*self.ani.F+weight0

    def test_losing_weight(self):
        """
        Test that the herbivores weight updates as it should
        """
        weight0 = self.ani.weight
        self.ani.losing_weight()
        assert weight0 == self.ani.weight+self.ani.eta*weight0

    @pytest.mark.parametrize("gamma,zeta,xi", [[0.1, 3.5, 1.2]])
    def test_birth1(self, gamma, zeta, xi, reset_params):
        """
        Testing whether the probability-statement in herbivore.birth() is functioning like it should.
        Since the weight of the "mother" in this instance is so low (10), it should always return 0.
        """
        num_herb = 100
        self.ani.herb_birth(num_herb)
        assert self.ani.prob == 0

    def test_birth2(self):
        """
        Testing whether the probability-statement in herbivore.birth() is functioning like it should.
        Since the weight of the "mother" in this instance is so high (100), it should always return 1
        (gamma * fitness * (num_herb - 1), and fitness is a function of age and weight).
        """
        gamma = 0.2
        zeta = 3.5
        xi = 1.2
        num_herb = 100
        ani = Herbivore(100, 5)
        ani.herb_birth(num_herb)
        assert ani.prob == 1


class Test_Guaranteed_birth:
    """
    Tests for situations with guaranteed birth
    """
    @pytest.fixture(autouse=True)
    def create_herb(self):
        """
        Creating a Herbivore to be used in testing
        """
        self.num_herb = 100
        self.ani = Herbivore(100, 5)

    def test_birth3(self):
        """
        Testing whether the probability-statement in herbivore.birth() is functioning like it should.
        Since the fitness of the mother is so high, the prob=1, and we are checking if the
        weight and fitness updates after giving birth
        """
        fitness0 = self.ani.fitness
        self.ani.herb_birth(self.num_herb)
        self.ani.update_fitness()
        assert self.ani.weight < 100 and self.ani.fitness < fitness0

    def test_gauss(self, mocker):
        """
        Checking whether the Gauss-distribution is implemented correctly
        """
        mocker.patch('random.gauss', return_value=5)
        ani2 = self.ani.herb_birth(self.num_herb)
        assert ani2.weight == 5

    def test_age(self):
        """
        Testing whether the age of an animal updates as it should.
        """
        age0 = self.ani.age
        self.ani.update_age()
        assert self.ani.age == age0 + 1

    def test_death1(self):
        """
        Testing if an animal dies if its weight is 0.
        """
        ani = Herbivore(0, 5)
        assert ani.death()

    def test_death2(self):
        """
        Testing to see if an animal survives if their fitness is 1.
        """
        ani = Herbivore(10, 5)
        ani.fitness = 1
        assert not ani.death()

    def test_set_params(self):
        """
        Testing to see if a KeyError is raised if the parameter is not part of the animal-class.
        """
        ani = Herbivore(20, 5)
        with pytest.raises(KeyError):
            ani.set_params({'delta': 0.5})


class Test_carnivores:
    """
    A class for testing carnivores
    """
    @pytest.fixture(autouse=True)
    def carn(self):
        """
        Making a Carnivore to use in tests
        """
        weight0 = 10
        age0 = 5
        self.ani = Carnivore(weight0, age0)

    @pytest.fixture(autouse=True)
    def reset_params(self):
        """
        resets the parameters in the Carnivore-class
        """
        yield
        Carnivore.set_params(Herbivore.default_params)

    def test_update_weight(self):
        """
        Testing that Carnivore update_weight also causes the fitness to increase
        """
        fitness0 = self.ani.fitness
        self.ani.eat(10)
        self.ani.update_fitness()
        assert fitness0 < self.ani.fitness

    @pytest.mark.parametrize("zeta", [0])
    def test_birth(self, zeta, mocker):
        """
        testing if the weight of a carnivore updates as it should.
        """
        self.ani.zeta = zeta
        weight0 = self.ani.weight
        mocker.patch('random.random', return_value=0)
        mocker.patch('random.gauss', return_value=1)
        self.ani.carn_birth(2)
        assert self.ani.weight < weight0

    def test_herb_killed(self, mocker):
        """
        testing if the herb_killed works as intended, with the herbivore having 0 fitness.
        """
        mocker.patch('random.random', return_value=0)
        self.ani.fitness = 1
        assert self.ani.herb_killed(0)

    def test_death(self):
        """
        testing if the Carnivore dies if their weight is 0
        """
        self.ani.weight = 0
        assert self.ani.death()
