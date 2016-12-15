import subprocess

# Import own modules
import config
import os
from support import hex_int


class Section:
    """A class representing a section in a map"""
    def __init__(self, f_map, line):
        tokens = line.split()

        self.name = tokens[0]
        if len(tokens) == 1:
            # Grab the next line and decode it
            line2 = next(f_map)
            tokens = line2.split()
            assert len(tokens) == 3, 'Can only handle entries of 3 tokens here!'
            self.address = hex_int(tokens[0])
            self.size = hex_int(tokens[1])
            self.obj = tokens[2]
        else:
            # Get the information from this line
            assert len(tokens) == 4, 'Can only handle entries of 4 tokens here!'
            self.address = hex_int(tokens[1])
            self.size = hex_int(tokens[2])
            self.obj = tokens[3]

class Map:
    """A class representing a map"""
    def __init__(self, map_path):
        with open(map_path, 'r') as f_map:
            self.discarded_sections = []
            self.pre_sections = []
            self.shuffle_sections = []
            self.post_sections = []

            # The map consists of several parts which we process differently
            target_sections = None
            for line in f_map:
                # Determine where in the map we are
                if 'Discarded input sections' in line:
                    target_sections = self.discarded_sections
                    continue

                if 'Memory Configuration' in line:
                    target_sections = None
                    continue

                if '*(.text.unlikely' in line:
                    target_sections = self.pre_sections
                    continue

                if '*(.text.[a-zA-Z0-9]*' in line:
                    target_sections = self.shuffle_sections
                    continue

                if '*(.text.*' in line:
                    target_sections = self.post_sections
                    continue

                # This is the farthest we go, anything behind this is not useful for us
                if '*(.gnu.warning)' in line:
                    break

                # We haven't arrived to the good part yet
                if target_sections is None:
                    continue

                # Look at all lines containing .text., but ignore some
                if '.text' in line and not '*' in line:
                    # Handle the line depending on where we are in the map
                    # Decode the entry into an object
                    target_sections.append(Section(f_map, line))

# Creates a linker script in which the text sections passed as an argument are placed in explicit order. If no sections are given, creates the default linker script.
def create_linker_script(sections):
    with open(os.path.join(config.tmp_dir, 'link.xc'), 'w') as f, open(os.path.join(config.ld_dir, 'ld1'), 'r') as ld1, open(os.path.join(config.ld_dir, 'ld2'), 'r') as ld2:
        # Write the first part
        f.write(ld1.read())

        # Write the shuffled array of sections
        if sections is not None:
            for section_list in sections:
                for section in section_list:
                    f.write('\t' + section + '\n')

        # Write the second part
        f.write(ld2.read())
