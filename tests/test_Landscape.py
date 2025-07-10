from biosim.landscape import Lowland, Highland, Desert, Water
import pytest


@pytest.fixture(autouse=True)
@pytest.mark.parametrize('class_to_test', [Lowland, Highland, Desert, Water])
def island_map(class_to_test):
    yield
    class_to_test.set_params(class_to_test.default_params)


@pytest.mark.parametrize('class_to_test', [Lowland, Highland, Desert, Water])
def test_set_param(class_to_test):
    """
    testing if the parameters updates for different landscapes.
    """
    landscape = class_to_test()
    food = True
    landscape.set_params({'food': food})
    assert landscape.food


@pytest.mark.parametrize('class_to_test', [Lowland, Highland, Desert, Water])
def test_set_param_error(class_to_test):
    """
    tests if the parameters raise a KeyError if the Key is not
    part of the landscapes parameters
    """
    landscape = class_to_test()
    rain = True
    with pytest.raises(KeyError):
        landscape.set_params({'rain': rain})
