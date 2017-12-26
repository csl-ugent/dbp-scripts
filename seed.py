class AbstractSeed:
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
        return type(self).__name__ + ': ' + str(self.seed)

    def __str__(self):
        return str(self.seed)

    # Static variables
    default_compile_options = []

# The different protections
from SP import SPSeed
from FS import FSSeed

nr_of_types = len(AbstractSeed.__subclasses__())

def get_types():
    return AbstractSeed.__subclasses__()
