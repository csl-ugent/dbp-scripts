class Seed:
    """A class a seed in general"""
    def __init__(self, seed):
        self.seed = seed

    def __bool__(self):
        return bool(self.seed)

    # This function will be called if we use the seed in random.seed()
    def __hash__(self):
        return self.seed

    def __int__(self):
        return self.seed

    def __repr__(self):
        return 'Seed: ' + str(self.seed) + ' Id: ' + str(self.idx)

    def __str__(self):
        return str(self.seed)

class SPSeed(Seed):
    """The class for SP seeds"""
    idx = len(Seed.__subclasses__())

class FSSeed(Seed):
    """The class for FS seeds"""
    idx = len(Seed.__subclasses__())

class NOPSeed(Seed):
    """The class for NOP seeds"""
    idx = len(Seed.__subclasses__())

nr_of_types = len(Seed.__subclasses__())

def get_types():
    return Seed.__subclasses__()
