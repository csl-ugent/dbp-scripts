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
    shuffled = base_symfile.funcs[base_symfile.nr_of_pre_funcs:-base_symfile.nr_of_post_funcs]
    random.shuffle(shuffled)
    base_symfile.funcs = base_symfile.funcs[:base_symfile.nr_of_pre_funcs] + shuffled + base_symfile.funcs[-base_symfile.nr_of_post_funcs:]

    # Fix up the addresses for every shuffled function
    for func in base_symfile.funcs[base_symfile.nr_of_pre_funcs:-base_symfile.nr_of_post_funcs]:
        # Predict the address of this section
        address = support.align(address, func.alignment)

        # Update the address of the function and all associated data
        func.update_address(address)

        # Go to the next function
        address = address + func.section_size

    # Fix up the addresses for every post function
    for func in base_symfile.funcs[-base_symfile.nr_of_post_funcs:]:
        # Update the address with the offset of the function
        address = address + func.offset

        # Update the address of the function and all associated data
        func.update_address(address)

def replay_nop(seed, base_symfile, base_data):
    print('************ Replaying NOP insertion. **********')

    # Use the replay tool to find the offsets on which NOPs were inserted for every section
    sections = {}
    for line in subprocess.check_output([os.path.join(config.replay_dir, 'nop'), str(seed), str(config.nop_chance), os.path.join(base_data, 'nopinsertion.list')], universal_newlines=True).splitlines():
        # If the line is the start of a new section, add it as an entry to the dictionary with a new list onto which insertions will be added.
        if ':' in line:
            assert line not in sections, 'Duplicate section!'
            insertions = []
            sections[line] = insertions
        else:
            insertions.append(support.hex_int(line))

    # For every function we get the offsets at which insertions happened, and update the corresponding lines to reflect this.
    # We'll keep the address offset introduced by the NOPs, and update all the lines with it. Insertions in the post functions
    # aren't replayed, as we lack the right information (section name) to do this.
    address_offset = 0
    for func in base_symfile.funcs[:-base_symfile.nr_of_post_funcs]:
        # Store the offset of the first line from the function address.
        first_line_offset = func.lines[0].address - func.address

        # Section/Function alignment might introduce changes to the address offset.
        address_offset = support.align(address_offset, func.alignment)

        insertions = sections.get(func.section_name, [])
        insertion_idx = 0 # Keeps track of how many insertions have been replayed.
        for line in func.lines:
            # Get the offset of the last instruction, and update the line
            line_offset = line.address - func.address + line.size -4
            line.update_address(address_offset)

            for insertion_offset in insertions[insertion_idx:]:
                # If the offset is located in the range belonging to the line, update some information.
                if insertion_offset < line_offset:
                    line.size += 4
                    address_offset += 4
                    insertion_idx += 1
                # If the offset is that of the last instruction, go to next insertion but don't update
                # the line size. When symfiles are generated for binaries with NOP insertion, a NOP inserted
                # at the end of a line is not considered to be part of the line.
                elif insertion_offset == line_offset:
                    address_offset += 4
                    insertion_idx += 1
                    break

                # Else we know the rest of the insertions are on later lines and we can break.
                else:
                    break

        # Rebuild function-wide information
        func.rebuild_meta_info(first_line_offset)

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
