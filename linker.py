import subprocess

# Import own modules
import config
import os
from support import hex_int

def gather_section_alignment(map_path, output_file):
    build_dir = os.path.dirname(map_path)
    with open(map_path, 'r') as f_map, open(output_file, 'w') as f_out:
        for line in f_map:
            # Find the lines that look like 'LOAD path'
            tokens = line.split()
            if len(tokens) != 2 or tokens[0] != 'LOAD':
                continue

            # Get the path, check whether it is an object or an archive
            path = tokens[1]
            if path.endswith('.o'):
                obj = True
            elif path.endswith('.a'):
                obj = False
            else:
                continue

            # If the path isn't already absolute, make it so by prepending the build directory
            if not os.path.isabs(path):
                path = os.path.join(build_dir, path)

            # If it's an object, write out its path
            if obj:
                f_out.write(path + '\n')

            # Get the objdump and filter the result, looking for .text sections (or or object file names in case of an archive)
            for line in subprocess.check_output(['objdump', '-h', path], universal_newlines=True).splitlines():
                if '.o:' in line and not obj:
                    obj_name = line.split(':')[0]
                    f_out.write(path + '(' + obj_name + ')\n')
                elif '.text' in line and not '.ARM.ex' in line:
                    tokens = line.split()
                    name = tokens[1]
                    powers = tokens[6].split('**')
                    alignment =  int(powers[0]) ** int(powers[1])
                    f_out.write(name + ' ' + str(alignment) + '\n')

class Section:
    """A class representing a section in a map"""
    def __init__(self, f_map, line, alignment_info):
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

        # If we can find the alignment, try to do so
        if alignment_info is not None:
            for obj in alignment_info.objects:
                if self.obj in obj.name:
                    self.alignment = obj.sections.get(self.name, None)
                    if self.alignment:
                        return

class AlignmentObject:
    """A class representing the alignment information for an object"""
    def __init__(self, name):
        self.name = name
        self.sections = {}

class AlignmentInformation:
    """A class representing the alignment information for a binary"""
    def __init__(self, align_path):
        self.objects = []

        with open(align_path, 'r') as f_align:
            align_lines = f_align.read().splitlines()

        for align_line in align_lines:
            # Check if this is an object (part of an archive or not)
            if align_line.endswith('.o') or align_line.endswith('.o)'):
                self.objects.append(AlignmentObject(align_line))
            # Otherwise it's a line to be part of the current object
            # Keep the section information in a dictionary
            else:
                tokens = align_line.split()
                self.objects[-1].sections[tokens[0]] = int(tokens[1])

class Map:
    """A class representing a map"""
    def __init__(self, map_path, align_path):
        # Load all section alignment information if it is present
        if align_path is not None:
            alignment_info = AlignmentInformation(align_path)
        else:
            alignment_info = None

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
                    target_sections.append(Section(f_map, line, alignment_info))

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

# Try to find the corresponding section if we can (can't be found for crtbegin objects for example).
def find_section_for_function(func, sections):
    for section in sections:
        if section.name == '.text.' + ' '.join(func.name):
            return section
    return None
