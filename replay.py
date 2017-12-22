import os
import random
import subprocess

# Import own modules
import config
import support

# We replay the shuffling of functions/sections using the seed, then predict the changes in addresses
# that occur due to alignment.
def replay_fs(seed, base_symfile, base_data):
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

def replay_sp(seed, base_symfile, base_data):
    print('************ Replaying stack padding. **********')

    # Use the replay tool to find the stack offset for every function
    sections = {}
    for line in subprocess.check_output([os.path.join(config.replay_dir, 'sp'), str(seed), str(config.max_padding),
        os.readlink(os.path.join(base_data, 'build')), os.path.join(base_data, 'stackpadding.list')], universal_newlines=True).splitlines():

        # Split the line and decode the tokens
        tokens = line.split()
        name = tokens[0]
        offset = int(tokens[1])

        # Add the section with the introduced diff
        assert name not in sections, 'Duplicate section!'
        sections[name] = offset

    # Use the replay tool again, but this time for the extra source code that was built
    for line in subprocess.check_output([os.path.join(config.replay_dir, 'sp'), str(seed), str(config.max_padding),
        os.path.join(config.extra_build_dir, '0', config.breakpad_archive), os.path.join(os.path.dirname(base_data), 'stackpadding.list')], universal_newlines=True).splitlines():

        # Split the line and decode the tokens
        tokens = line.split()
        name = tokens[0]
        offset = int(tokens[1])

        # Add the section with the introduced diff
        assert name not in sections, 'Duplicate section!'
        sections[name] = offset

    for func in base_symfile.funcs:
        # Get the stack offset introduced
        offset = sections.get(func.section_name, 0)

        if offset:
            base_record = func.get_stack_offset_record()
            # This record may very well not exist, such as when a frame pointer is used.
            if base_record:
                base_record.set_frame_size(base_record.get_frame_size() + offset - config.default_padding)
