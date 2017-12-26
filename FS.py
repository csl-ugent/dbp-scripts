import random

# Import own modules
import support
from seed import AbstractSeed

class FSSeed(AbstractSeed):
    """The class for FS seeds"""
    idx = len(AbstractSeed.__subclasses__())

    # We replay the shuffling of functions/sections using the seed, then predict the changes in addresses
    # that occur due to alignment.
    def replay(seed, base_symfile, base_data):
        print('************ Replaying function shuffling. **********')

        # Get the start address for the shuffle functions
        address = base_symfile.funcs[base_symfile.nr_of_pre_funcs].address

        # Select the shuffle functions, shuffle them, then reconstitute the array including those pre- and post- parts that stay in the same order
        random.seed(seed)
        shuffled = base_symfile.funcs[base_symfile.nr_of_pre_funcs:base_symfile.post_funcs_idx]
        random.shuffle(shuffled)
        base_symfile.funcs = base_symfile.funcs[:base_symfile.nr_of_pre_funcs] + shuffled + base_symfile.funcs[base_symfile.post_funcs_idx:]

        # Fix up the addresses for every shuffled function
        for func in base_symfile.funcs[base_symfile.nr_of_pre_funcs:base_symfile.post_funcs_idx]:
            # Predict the address of this section
            address = support.align(address, func.alignment)

            # Update the address of the function and all associated data
            func.update_address(address)

            # Go to the next function
            address = address + func.section_size

        # Fix up the addresses for every post function
        for func in base_symfile.funcs[base_symfile.post_funcs_idx:]:
            # Update the address with the offset of the function
            address = address + func.offset

            # Update the address of the function and all associated data
            func.update_address(address)
