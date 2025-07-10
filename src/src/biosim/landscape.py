class Lowland:
    """
    A class for the Lowland-landscape in BioSim.
    """
    f_max = 700  # max amount of fodder on the tile
    traversable = True
    food = True
    type = "L"
    default_params = {'f_max': f_max, 'traversable': traversable, 'food': food, 'type': type}

    @classmethod
    def set_params(cls, new_params):
        """
        :new_params: dict of new parameters
        """
        for key in new_params:
            if key not in ('f_max', 'traversable', 'food', 'type'):
                raise KeyError('Invalid parameter name: ' + key)

        if 'f_max' in new_params:
            cls.f_max = new_params['f_max']
        if 'traversable' in new_params:
            cls.traversable = new_params['traversable']
        if 'food' in new_params:
            cls.food = new_params['food']
        if 'L' in new_params:
            cls.type = new_params['type']


class Highland:
    """
    A class for the Highland-landscape in BioSim.
    """
    f_max = 300
    traversable = True
    food = True
    type = 'H'
    default_params = {'f_max': f_max, 'traversable': traversable, 'food': food, 'type': type}

    @classmethod
    def set_params(cls, new_params):
        """
        :new_params: dict of new parameters
        """
        for key in new_params:
            if key not in ('f_max', 'traversable', 'food', 'type'):
                raise KeyError('Invalid parameter name: ' + key)

        if 'f_max' in new_params:
            cls.f_max = new_params['f_max']
        if 'traversable' in new_params:
            cls.traversable = new_params['traversable']
        if 'food' in new_params:
            cls.food = new_params['food']
        if 'H' in new_params:
            cls.type = new_params['type']


class Water:
    """
    A class for the water-landscape in BioSim.
    """
    traversable = False
    food = False
    type = 'W'
    default_params = {'traversable': traversable, 'food': food, 'type': type}

    @classmethod
    def set_params(cls, new_params):
        """
        :new_params: dict of new parameters
        """
        for key in new_params:
            if key not in ('traversable', 'food','type'):
                raise KeyError('Invalid parameter name: ' + key)

        if 'traversable' in new_params:
            cls.traversable = new_params['traversable']
        if 'food' in new_params:
            cls.food = new_params['food']
        if 'W' in new_params:
            cls.type = new_params['type']


class Desert:
    """
    A class for the desert-landscape in BioSim.
    """
    traversable = True
    food = False
    type = 'D'
    default_params = {'traversable': traversable, 'food': food, 'type': type}

    @classmethod
    def set_params(cls, new_params):
        """
        :new_params: dict of new parameters
        """
        for key in new_params:
            if key not in ('traversable', 'food', 'type'):
                raise KeyError('Invalid parameter name: ' + key)

        if 'traversable' in new_params:
            cls.traversable = new_params['traversable']
        if 'food' in new_params:
            cls.food = new_params['food']
        if 'D' in new_params:
            cls.type = new_params['type']
