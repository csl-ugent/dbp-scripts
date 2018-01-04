import glob
import os
import subprocess

# Import own modules
import config
import support
from seed import AbstractSeed

class NOPSeed(AbstractSeed):
    """The class for NOP seeds"""
    idx = len(AbstractSeed.__subclasses__())

    # Static variables
    opportunity_log = 'nopinsertion.list'

    def diversify_build(seed):
        return ['-mllvm', '-nopinsertion_chance=' + str(config.nopinsertion_chance), '-mllvm', '-nopinsertion_seed=' + str(seed)]

    def replay(seed, base_symfile, base_data):
        print('************ Replaying NOP insertion. **********')

        # Use the replay tool to find the offsets on which NOPs were inserted for every section.
        # We do a replay for the opportunity log of the actual build, and also of that for every
        # extra (shared) artefact.
        sections = {}
        seed.run_replay_tool(sections, os.readlink(os.path.join(base_data, 'build')), os.path.join(base_data, seed.opportunity_log))
        shared_base_data = os.path.dirname(base_data)
        for build_prefix in glob.glob(os.path.join(shared_base_data, 'build.*')):
            suffix = build_prefix[build_prefix.rfind('.'):]
            seed.run_replay_tool(sections, os.readlink(build_prefix), os.path.join(os.path.dirname(base_data), seed.opportunity_log + suffix))

        # For every function we get the offsets at which insertions happened, and update the corresponding lines to reflect this.
        # We'll keep the address offset introduced by the NOPs, and update all the lines with it.
        address_offset = 0
        new_func_address = base_symfile.funcs[0].address
        for func in base_symfile.funcs:
            # Section/Function alignment might introduce changes to the address offset.
            func.calculate_lineless_area()
            new_func_address = support.align(new_func_address, func.alignment)
            address_offset = new_func_address - func.address

            # We keep a list of offsets introduced to all the stack records by insertions in this function
            stack_offsets = [0] * len(func.stacks)

            # Get the insertions for this function
            insertions = sections.get(func.section_name, [])
            insertion_idx = 0 # Keeps track of how many insertions have been replayed.

            # We start by replaying those insertions that happen before the first line record, increasing the size of the
            # lineless area. We keep track of this increase, but don't apply it yet (so we can do a correct comparison
            # of offsets).
            lineless_size_increase = 0
            for insertion_idx, insertion in enumerate(insertions):
                offset, size_diff = insertion
                if offset >= func.lineless_size:
                    break

                lineless_size_increase += size_diff
                address_offset += size_diff

                # Adjust any stack records within the function, after the insertion
                for iii, stack in enumerate(func.stacks):
                    if (func.address + offset) < stack.address:
                        stack_offsets[iii] += size_diff

            # If the loop completes without breaking, all insertions were replayed. To prevent the next loop
            # from erroneously restarting at the last insertion, increase the index.
            else:
                insertion_idx += 1

            # Now we've performed all insertions located before the first line, actually increase the lineless size.
            func.lineless_size += lineless_size_increase

            # Now we can replay those insertions happening inside the line records, while updating these lines.
            for line in func.lines:
                # Get the offset of the last instruction, and update the line
                line_offset = line.address - func.address + line.size
                line.update_address(address_offset)

                # While the insertion is located in the range belonging to the line, update some information to reflect it.
                while insertion_idx < len(insertions):
                    offset, size_diff = insertions[insertion_idx]
                    if offset < line_offset:
                        line.size += size_diff
                        address_offset += size_diff

                        # Adjust any stack records within the function, after the NOP
                        for iii, stack in enumerate(func.stacks):
                            if (func.address + offset) < stack.address:
                                stack_offsets[iii] += size_diff

                        insertion_idx += 1
                    else:
                        break

            # Perform the actual adjustment to the stack records
            for stack, stack_offset in zip(func.stacks, stack_offsets):
                stack.address += stack_offset

            # Rebuild function-wide information
            func.rebuild_meta_info(new_func_address)
            new_func_address = func.address + func.size

    def run_replay_tool(seed, sections, build_prefix, opportunity_log):
        for line in subprocess.check_output([os.path.join(config.replay_dir, 'nop'), str(seed), str(config.nopinsertion_chance),
            build_prefix, opportunity_log], universal_newlines=True).splitlines():
            # If the line is the start of a new section, add it as an entry to the dictionary with a new list onto which insertions will be added.
            if ':' in line:
                assert line not in sections, 'Duplicate section!'
                insertions = []
                sections[line] = insertions
            else:
                # For any insertion, the get offset at which it happens, and the size change it induces
                tokens = line.split()
                insertions.append((support.hex_int(tokens[0]), support.hex_int(tokens[1])))
