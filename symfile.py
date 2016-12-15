import os

# Import own modules
from operator import attrgetter
from support import hex_int
from support import hex_str

class Location:
    """A class representing a source file location"""
    def __init__(self, linenr, filenum):
        self.linenr = linenr
        self.filenum = filenum

    def __eq__(self, other):
        if self.linenr != other.linenr:
            return False
        if self.filenum != other.filenum:
            return False
        return True

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return ' '.join((str(self.linenr), str(self.filenum)))

class Line:
    """A class representing a line record"""
    def __init__(self, line):
        tokens = line.split()
        self.address = hex_int(tokens[0])
        self.size = hex_int(tokens[1])
        self.location = Location(int(tokens[2]), int(tokens[3]))

    def __eq__(self, other):
        if self.address != other.address:
            return False
        if self.size != other.size:
            return False
        if self.location != other.location:
            return False

        return True

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return ' '.join((hex_str(self.address), hex_str(self.size), str(self.location)))

    def same_pos(self, other):
        return self.location == other.location

    # Update the address for a line, and all other data associated with it (which is nothing anymore at this point)
    def update_address(self, offset):
        self.address = self.address + offset

class Function:
    """A class representing a function record"""
    def __init__(self, line):
        self.lines = []
        tokens = line.split()
        self.address = hex_int(tokens[1])
        self.size = hex_int(tokens[2])
        self.parameter_size = hex_int(tokens[3])
        self.name = tokens[4:]

        # Data will be added onto these later on
        self.publics = []
        self.stacks = []

    def __eq__(self, other):
        if self.address != other.address:
            return False
        if self.size != other.size:
            return False
        if self.parameter_size != other.parameter_size:
            return False
        if self.name != other.name:
            return False
        if self.lines != other.lines:
            return False
        if self.stack_init != other.stack_init:
            return False
        if self.stacks != other.stacks:
            return False
        return True

    def __ne__(self, other):
        return not self == other

    def add_line_record(self, line):
        self.lines.append(Line(line))

    # Get the stack record containing the stack offset
    def get_stack_offset_record(self):
        for stack in reversed(self.stacks):
            # Check whether the signature of the entry matches and if it does, return it
            if len(stack.entries) == 4 and stack.entries[0] == '.cfa:' and stack.entries[1] == 'sp' and stack.entries[3] == '+':
                return stack

        return None

    # Rebuild the meta information (address, size, meta records) using the values of the lines
    # and the offset between the start of the function and the first line.
    def rebuild_meta_info(self, first_line_offset):
        new_address = self.lines[0].address - first_line_offset
        func_offset = new_address - self.address
        self.address = new_address
        self.size = (self.lines[-1].address - self.address) + self.lines[-1].size
        self.update_meta_records(func_offset)

    # Update the address for a function and its lines
    def update_address(self, address):
        offset = address - self.address
        self.address = address
        self.update_meta_records(offset)
        for line in self.lines:
            line.update_address(offset)

    def update_meta_records(self, offset):
        # Set the information for the STACK CFI INIT record
        self.stack_init.address = self.address
        self.stack_init.size = self.size

        # Add the offset for all stack records and public records
        for stack in self.stacks:
            stack.address = stack.address + offset
        for public in self.publics:
            public.address = public.address + offset

    def __repr__(self):
        res = ' '.join(('FUNC', hex_str(self.address), hex_str(self.size), hex_str(self.parameter_size), ' '.join(self.name))) + '\n'
        for line in self.lines:
            res = res + str(line) + '\n'

        return res

class Public:
    """A class representing a public record"""
    def __init__(self, line):
        tokens = line.split()
        self.address = hex_int(tokens[1])
        self.parameter_size = hex_int(tokens[2])
        self.name = tokens[3:]

    def __eq__(self, other):
        if self.address != other.address:
            return False
        if self.parameter_size != other.parameter_size:
            return False
        if self.name != other.name:
            return False
        return True

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return ' '.join(('PUBLIC', hex_str(self.address), hex_str(self.parameter_size), ' '.join(self.name)))

class Stack:
    """A class representing a stack record"""
    def __init__(self, line):
        tokens = line.split()
        # Decode INIT records and other records differently
        if tokens[2] == 'INIT':
            self.address = hex_int(tokens[3])
            self.size = hex_int(tokens[4])
            self.entries = tokens[5:]
        else:
            self.address = hex_int(tokens[2])
            self.size = 0
            self.entries = tokens[3:]

    def __eq__(self, other):
        if self.address != other.address:
            return False
        if self.size != other.size:
            return False
        if self.entries != other.entries:
            return False
        return True

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        if self.size != 0:
            return ' '.join(('STACK CFI INIT', hex_str(self.address), hex_str(self.size), ' '.join(self.entries)))
        else:
            return ' '.join(('STACK CFI', hex_str(self.address), ' '.join(self.entries)))

    def get_frame_size(self):
        return int(self.entries[2])

    def set_frame_size(self, size):
        self.entries[2] = str(size)

class SymFile:
    """A class representing a symfile"""
    def __init__(self):
        self.files = []
        self.funcs = []
        self.publics = []
        self.unassociated_publics = []
        self.stacks = []
        self.unassociated_stacks = []

    def __eq__(self, other):
        # Copy function lists, order on address, and compare
        a = self.funcs
        b = other.funcs
        a.sort(key=attrgetter('address'))
        b.sort(key=attrgetter('address'))
        if a != b:
            return False

        # Copy public lists, order on address, and compare
        a = self.publics
        b = other.publics
        a.sort(key=attrgetter('address'))
        b.sort(key=attrgetter('address'))
        if a != b:
            return False

        return True

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        res = self.module
        for fi in self.files:
            res = res + str(fi)
        for func in self.funcs:
            res = res + str(func)
        self.publics.sort(key=attrgetter('address'))
        for public in self.publics:
            res = res + str(public) + '\n'
        for stack in self.stacks:
            res = res + str(stack) + '\n'
        return res

    # Augment the symfile with information from the linkermap
    def augment(self, linkermap, build_dir):
        # Determine how many of each kind of functions there are
        self.nr_of_pre_funcs = len(linkermap.pre_sections)
        self.nr_of_shuffle_funcs = len(linkermap.shuffle_sections)
        self.nr_of_post_funcs = len(self.funcs) - self.nr_of_shuffle_funcs - self.nr_of_pre_funcs

        # For the pre functions we have section information, copy it over to the functions
        for (func, section) in zip(self.funcs[:self.nr_of_pre_funcs], linkermap.pre_sections):
            func.alignment = section.alignment
            func.section_size = section.size
            func.section_name = os.path.join(build_dir, section.obj) + ':' + section.name

        # For the shuffle functions we have section information, copy it over to the functions.
        for (func, section) in zip(self.funcs[self.nr_of_pre_funcs:-self.nr_of_post_funcs], linkermap.shuffle_sections):
            func.alignment = section.alignment
            func.section_size = section.size
            func.section_name = os.path.join(build_dir, section.obj) + ':' + section.name

        # For the functions at the end, there was no ffunction-sections. Therefore, with possibly multiple functions in a section, we have no information
        # on function alignment/size and will use defaults. We will attempt to determine offsets though from the previous function though.
        if self.nr_of_post_funcs:
            # Get the address at the end of the last shuffled section
            address = self.funcs[-self.nr_of_post_funcs -1].address + linkermap.shuffle_sections[-1].size
            for func in self.funcs[-self.nr_of_post_funcs:]:
                # Get the offset between its address and the address of the last known function
                func.offset = func.address - address
                address = func.address

                # Try to find the corresponding section (can't be found for crtbegin objects for example) and use
                # its information. If we can't find it, use some default values.
                func_section = None
                for section in linkermap.post_sections:
                    if section.name == '.text.' + ' '.join(func.name):
                        func_section = section
                        break

                if func_section:
                    func.alignment = func_section.alignment
                    func.section_size = func_section.size
                    func.section_name = os.path.join(build_dir, func_section.obj) + ':' + func_section.name
                else:
                    func.alignment = 4
                    func.section_size = func.size
                    func.section_name = None

    # Return the Function that is at this address, or None if nothing is found
    def get_func_by_address(self, address):
        for func in self.funcs:
            if func.address == address:
                return func

        return None

    def get_func_containing_address(self, address):
        for func in self.funcs:
            if func.address <= address and address < (func.address + func.size):
                return func

        return None

    # Return the Function associated with a public symbol's address
    def get_func_public(self, address):
        for func in self.funcs:
            if func.address <= address and address < (func.address + func.size):
                return func

        # The line might be before the first function or behind the last function. If it's
        # before the first function we can return None as this address does not have to be updated.
        # If it's behind the last function we simply return the last line of the last function.
        if address < self.funcs[0].address:
            return None
        else:
            return self.funcs[-1]

    # The constructor to create a SymFile by reading it in from a path
    @classmethod
    def read_f(cls, path):
        with open(path, 'r') as f:
            return cls.read(f)

    # The constructor to create a SymFile by reading it in from a file
    @classmethod
    def read(cls, f):
        self = cls()
        for line in f:
            # Get the type of this record
            record_type = line.split()[0]

            # Handle a module record (there can be only one)
            if record_type == 'MODULE':
                self.module = line

            # Handle a file record (there's a number of them, but we don't expect to ever change them)
            elif record_type == 'FILE':
                self.files.append(line)

            # Handle a public symbol
            elif record_type == 'PUBLIC':
                self.publics.append(Public(line))

            # Handle a function record. We create a new instance of the Function class and append it to the list.
            elif record_type == 'FUNC':
                self.funcs.append(Function(line))

            # Handle a stack (CFI) record.
            elif record_type == 'STACK':
                assert line.split()[1] == 'CFI', 'We can only handle STACK CFI frames.'
                self.stacks.append(Stack(line))

            # Handle a line record, let the Function class handle it.
            else:
                self.funcs[-1].add_line_record(line)

        # Sort the functions by address
        self.funcs.sort(key=attrgetter('address'))

        # Associate all stack records to lines or functions (except for those with negative addresses).
        for stack in (stack for stack in self.stacks if stack.address < 0x8000000):
            # If it's an INIT record we should be able to associate it to a function. If None
            # is found this means it corresponds to one of the unnamed post functions.
            if stack.size:
                func = self.get_func_by_address(stack.address)
                if func:
                    func.stack_init = stack
                else:
                    self.unassociated_stacks.append(stack)
            else:
                # Try to find the function that contains the stack record's address.
                func = self.get_func_containing_address(stack.address)
                if func:
                    func.stacks.append(stack)
                else:
                    self.unassociated_stacks.append(stack)

        # Associate all publics to lines (except for those with negative addresses).
        for public in (public for public in self.publics if public.address < 0x8000000):
            func = self.get_func_public(public.address)
            if func:
                func.publics.append(public)
            else:
                self.unassociated_publics.append(public)

        return self

    # Write to a path
    def write_f(self, path):
        with open(path, 'w') as f:
            self.write(f)

    # Write to a file
    def write(self, f):
        f.write(str(self))
