import io
import subprocess

# Import own modules
import config
from support import hex_int
from symfile import SymFile
from support import hex_str

def update_symfile_with_listing(symfile, listing_path, old_base, new_base):
    # Create the mapping between new and old offsets in the symfile
    mapping = {}
    with open(listing_path, 'r') as f_list:
        for line in f_list:
            tokens = line.split()
            if tokens[0] == 'New':
                new_address = hex_int(tokens[1])
                old_address = hex_int(tokens[3])
            elif tokens[0].startswith('0x'):# In this exceptional case, new and old are the same
                new_address = hex_int(tokens[0])
                old_address = new_address
            else:
                continue

            new_offset = new_address - new_base
            old_offset = old_address - old_base
            mapping[old_offset] = new_offset

    # Iterate over all functions to update the addresses using the mapping. We will also update the size
    # of the lines. To do this we iterate over all functions/lines in a reverse order, so that at all times
    # we have the (new) address of the next line. We initialize the next address with a fictitious address
    # that lies right behind the last instruction of the binary (whose address is the last new_address).
    next_address = new_address + 4
    new_funcs = []
    for func in reversed(symfile.funcs):
        # Store the offset of the first line from the function address.
        first_line_offset = func.lines[0].address - func.address

        new_lines = []
        for line in reversed(func.lines):
            if line.address in mapping:
                # Update the line. We get the new address of the last instruction and use to determine
                # the size of the line. If this address is past the address of the next line however,
                # (as might happen for some data instruction from a pool) we'll use the next address to
                # determine the size. If a NOP is inserted right behind the last instruction it won't be
                # considered to be part of this line.
                end_address = mapping[line.address + line.size -4]
                line.address = mapping[line.address]
                if end_address < next_address:
                    line.size = end_address - line.address +4
                else:
                    line.size = next_address - line.address

                # Update next address and append line
                next_address = line.address
                new_lines.append(line)

        # If we still have lines the function is extant and will be kept, otherwise its meta-information is removed.
        if new_lines:
            func.lines = list(reversed(new_lines))
            new_funcs.append(func)
            func.rebuild_meta_info(first_line_offset)
            next_address = func.address
        else:
            for public in func.publics:
                symfile.publics.remove(public)
            for stack in func.stacks:
                symfile.stacks.remove(stack)

    # Update the addresses of the unassociated public and stack records
    for public in symfile.unassociated_publics:
        public.address = mapping[public.address]
    for stack in symfile.unassociated_stacks:
        stack.address = mapping[stack.address]

# We can't directly create a symfile for binaries that were rewritten using Diablo. Therefore we'll create a symfile
# from the binary that served as input to Diablo, and then update this symfile using the instruction listing outputted
# by Diablo.
def create_updated_symfile(binary, listing_path, f_out):
    # Dump the symfile from the binary and read it into a SymFile
    with io.StringIO(subprocess.check_output([config.dump_syms, binary], stderr=subprocess.DEVNULL, universal_newlines=True)) as f_tmp:
        symfile = SymFile.read(f_tmp)

    # Update the symfile using the instruction listing and write it out
    update_symfile_with_listing(symfile, listing_path, config.base_address, config.base_address)
    symfile.write(f_out)
