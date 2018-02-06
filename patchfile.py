from difflib import SequenceMatcher
import itertools

# Import own modules
import support
from support import hex_int
from support import hex_str
from symfile import Line

class AdditionPatch:
    def __init__(self, offset, lines):
        self.lines = lines
        self.offset = offset

    def __repr__(self):
        res = 'Add ' + hex_str(len(self.lines)) + ' lines at ' + hex_str(self.offset) + '\n'
        for line in self.lines:
            res += str(line) + '\n'
        return res

    def __str__(self):
        res = 'A' + hex_str(len(self.lines)) + '\n'
        for line in self.lines:
            res += str(line) + '\n'
        return res

    def apply(self, func, offset):
        func.lines = func.lines[:offset] + self.lines + func.lines[offset:]
        self.update_address_offset()
        return (len(self.lines), len(self.lines), sum([line.size for line in self.lines]))

    @classmethod
    def create(cls, offset, lines):
        self = cls(offset, lines)
        self.update_address_offset()
        return self

    @classmethod
    def read(cls, offset, header, lines):
        if header.startswith('A'):
            size = hex_int(header[1:])
            added_lines = []
            for line in lines[:size]:
                added_lines.append(Line(line))

            return (size, cls(offset, added_lines))
        else:
            return (0, None)

    # Update the global address offset according to the changes introduced by this patch
    def update_address_offset(self):
        global address_offset
        for line in self.lines:
            address_offset += line.size

class DeletionPatch:
    def __init__(self, offset, size):
        self.offset = offset
        self.size = size

    def __repr__(self):
        res = 'Delete ' + hex_str(self.size) + ' lines at ' + hex_str(self.offset) + '\n'
        for line in self.lines:
            res += str(line) + '\n'
        return res

    def __str__(self):
        return 'D' + hex_str(self.size) + '\n'

    def apply(self, func, offset):
        self.lines = func.lines[offset:offset + self.size]
        size_diff = -sum([line.size for line in self.lines])
        del func.lines[offset:offset + self.size]
        self.update_address_offset()
        return (-self.size, 0, size_diff)

    @classmethod
    def create(cls, offset, lines):
        self = cls(offset, len(lines))
        self.lines = lines
        self.update_address_offset()
        return self

    @classmethod
    def read(cls, offset, header, lines):
        if header.startswith('D'):
            size = hex_int(header[1:])
            return (0, cls(offset, size))
        else:
            return (0, None)

    # Update the global address offset according to the changes introduced by this patch
    def update_address_offset(self):
        global address_offset
        for line in self.lines:
            address_offset -= line.size

class LinePatch:
    def __init__(self, offset, address_diff, size_diff):
        self.offset = offset
        self.address_diff = address_diff
        self.size_diff = size_diff

    def __repr__(self):
        res = 'Change line at ' + hex_str(self.offset) + '\n'
        res += 'Address diff: ' + hex_str(self.address_diff) + '\n'
        res += 'Size diff: ' + hex_str(self.size_diff) + '\n'
        return res

    def __str__(self):
        res = 'L'
        if self.address_diff:
            res += hex_str(self.address_diff)
        res += ':'
        if self.size_diff:
            res += hex_str(self.size_diff)
        return res + '\n'

    def apply(self, func, offset):
        line = func.lines[offset]
        line.update_address(address_offset + self.address_diff)
        line.size = line.size + self.size_diff
        self.update_address_offset()
        return (0, 1, self.size_diff)

    @classmethod
    def create(cls, offset, base, div):
        # Use address offset in calculation, and update it
        address_diff = div.address - (base.address + address_offset)
        size_diff = div.size - base.size
        self = cls(offset, address_diff, size_diff)
        self.update_address_offset()
        return self

    @classmethod
    def read(cls, offset, header, lines):
        if header.startswith('L'):
            # Decode the line, if a string is empty the diff is 0
            tokens = header[1:].split(':')
            address_diff = hex_int(tokens[0]) if tokens[0] else 0
            size_diff = hex_int(tokens[1]) if tokens[1] else 0

            return (0, cls(offset, address_diff, size_diff))
        else:
            return (0, None)

    # Update the global address offset according to the changes introduced by this patch
    def update_address_offset(self):
        global address_offset
        address_offset += self.size_diff + self.address_diff

class SubstitutionPatch:
    def __init__(self, offset, added_lines, deleted_size):
        self.offset = offset
        self.added_lines = added_lines
        self.deleted_size = deleted_size

    def __repr__(self):
        res = 'Substitute ' + hex_str(self.deleted_size) + ' lines for ' + hex_str(len(self.added_lines)) + ' lines at ' + hex_str(self.offset) + '\n'
        for line in self.deleted_lines:
            res += str(line) + '\n'
        res += 'For:\n'
        for line in self.added_lines:
            res += str(line) + '\n'
        return res

    def __str__(self):
        res = 'S' + hex_str(self.deleted_size) + ':' + hex_str(len(self.added_lines)) + '\n'
        for line in self.added_lines:
            res += str(line) + '\n'
        return res

    def apply(self, func, offset):
        self.deleted_lines = func.lines[offset:offset + self.deleted_size]
        size_diff = sum([line.size for line in self.added_lines]) - sum([line.size for line in self.deleted_lines])
        func.lines = func.lines[:offset] + self.added_lines + func.lines[offset + self.deleted_size:]
        self.update_address_offset()
        return (len(self.added_lines) - self.deleted_size, len(self.added_lines), size_diff)

    @classmethod
    def create(cls, offset, added_lines, deleted_lines):
        self = cls(offset, added_lines, len(deleted_lines))
        self.deleted_lines = deleted_lines
        self.update_address_offset()
        return self

    @classmethod
    def read(cls, offset, header, lines):
        if header.startswith('S'):
            tokens = header[1:].split(':')
            deleted_size = hex_int(tokens[0])
            added_size = hex_int(tokens[1])
            added_lines = []
            for line in lines[:added_size]:
                added_lines.append(Line(line))

            return (added_size, cls(offset, added_lines, deleted_size))
        else:
            return (0, None)

    def update_address_offset(self):
        # Update the address offset
        global address_offset
        for line in self.added_lines:
            address_offset += line.size
        for line in self.deleted_lines:
            address_offset -= line.size

class StackPatch:
    def __init__(self, size_diff, address_diff):
        self.address_diff = address_diff
        self.size_diff = size_diff

    def __repr__(self):
        return 'Patch the stack offset record with size difference: ' + hex_str(self.size_diff) + ' and address difference: ' + hex_str(self.address_diff) + '\n'

    def __str__(self):
        if self.size_diff:
            res = hex_str(self.size_diff // 8)
        else:
            res = ''
        if self.address_diff:
            res += ':' + hex_str(self.address_diff)

        return res

    def apply(self, func_base):
        base_record = func_base.get_stack_offset_record()

        assert base_record, 'Trying to apply a stack patch when no stack offset record is present!'
        base_record.address += self.address_diff
        base_record.set_frame_size(base_record.get_frame_size() + self.size_diff)

    @classmethod
    def create(cls, func_base, func_div):
        base_record = func_base.get_stack_offset_record()
        div_record = func_div.get_stack_offset_record()

        # The arguments can be None, but only when they are both so.
        assert bool(base_record) == bool(div_record), 'One of the functions has stack offset record while the other does not. This can not happen.'

        # If both arguments are None, we don't need a patch
        if base_record is None and div_record is None:
            return None

        # Determine the differences and create the patch
        size_diff = div_record.get_frame_size() - base_record.get_frame_size()
        div_offset = div_record.address - func_div.address
        base_offset = base_record.address - func_base.address
        address_diff = div_offset - base_offset
        if size_diff or address_diff:
            return cls(size_diff, address_diff)
        else:
            return None

    @classmethod
    def read(cls, header):
        tokens = header.split(':')
        if len(tokens) == 2:
            size_diff = hex_int(tokens[0]) * 8 if tokens[0] else 0
            address_diff = hex_int(tokens[1])
        else:
            size_diff = hex_int(tokens[0]) * 8
            address_diff = 0
        return cls(size_diff, address_diff)

class FuncPatch:
    """A class representing a function patch"""
    def __init__(self, name):
        self.patches = []
        self.name = name
        self.stack_patch = None

    def __repr__(self):
        res = 'FUNC PATCH ' + ' '.join(self.name) + '\n'
        if self.stack_patch:
            res += repr(self.stack_patch)
        for patch in self.patches:
            res += repr(patch)
        return res

    def __str__(self):
        # If it exists, encode the stack offset in the function patch header. Else simply finish the header.
        if self.stack_patch:
            res = str(self.stack_patch) + '\n'
        else:
            res = '\n'

        # We encode the relative offsets between patches in such a way that two patches on two lines right after each other have offset 0
        # If the offset is 0 we don't encode it.
        prev_offset = -1
        for patch in self.patches:
            rel_offset = patch.offset - prev_offset -1
            if rel_offset:
                res += hex_str(rel_offset)
            res += str(patch)
            prev_offset = patch.offset
        return res

    def apply(self, func):
        # Section/Function alignment might introduce changes to the address offset.
        self.update_address_offset(func.alignment)

        # Apply the stack patch, if any
        if self.stack_patch:
            self.stack_patch.apply(func)

        func.calculate_lineless_area()
        new_func_address = func.address + address_offset

        # We keep a list of offsets introduced to all the stack records by line changes
        stack_offsets = [0] * len(func.stacks)

        line_offset = 0 # Track the running offset introduced by the patches
        update_offset = 0 # Track the offset from which we should start updating addresses
        for patch in self.patches:
            # Determine the offset of this patch in the (current, modified) list of lines
            offset = patch.offset + line_offset

            # Update all intermediate lines (that are not to be patched) with the address offset
            for line in func.lines[update_offset:offset]:
                line.update_address(address_offset)

            # Get the farthest address that, after the patch, will be fixed
            patch_line = func.lines[offset] if offset < len(func.lines) else None
            patch_address = patch_line.address + patch_line.size if patch_line else func.address + func.size

            # Apply the actual patch and receive its results. Then update the offsets using this information.
            (patch_offset, patch_size, size_diff) = patch.apply(func, offset)
            line_offset += patch_offset
            update_offset = offset + patch_size

            # Adjust any stack records within the function that are found after the patch address.
            for iii, stack in enumerate(func.stacks):
                if patch_address < stack.address:
                    stack_offsets[iii] += size_diff

        # Finish updating addresses
        for line in func.lines[update_offset:]:
            line.update_address(address_offset)

        # Perform the actual adjustment to the stack records. Don't touch the
        # stack offset record. This is handled separately by StackPatches.
        stack_offset_record = func.get_stack_offset_record()
        for stack, stack_offset in zip(func.stacks, stack_offsets):
            if not stack_offset_record or stack != stack_offset_record:
                stack.address += stack_offset

        # Rebuild function-wide information
        func.rebuild_meta_info(new_func_address)

    # Constructor to create a FunctionPatch by diffing two Function instances
    @classmethod
    def create(cls, func_base, func_div):
        assert func_base.name == func_div.name, "Creating a patch from two different functions!"
        self = cls(func_base.name)

        # Section/Function alignment might introduce changes to the address offset. Align it.
        cls.update_address_offset(func_base.alignment)

        # Create the stack patch
        self.stack_patch = StackPatch.create(func_base, func_div)

        # Get all the lines' locations and use these to diff
        base_locs = [line.location for line in func_base.lines]
        div_locs = [line.location for line in func_div.lines]
        for tag, i1, i2, j1, j2 in SequenceMatcher(None, base_locs, div_locs, autojunk=False).get_opcodes():
            if tag == 'insert':
                self.patches.append(AdditionPatch.create(i1, func_div.lines[j1:j2]))

            elif tag == 'delete':
                self.patches.append(DeletionPatch.create(i1, func_base.lines[i1:i2]))

            elif tag == 'replace':
                self.patches.append(SubstitutionPatch.create(i1, func_div.lines[j1:j2], func_base.lines[i1:i2]))

            elif tag == 'equal':
                for base_offset, (base_line, div_line) in enumerate(zip(func_base.lines[i1:i2], func_div.lines[j1:j2]), i1):
                    if (base_line.address + address_offset) != div_line.address or base_line.size != div_line.size:
                        self.patches.append(LinePatch.create(base_offset, base_line, div_line))

        return self

    # Constructor to create a FunctionPatch from a file
    @classmethod
    def read(cls, lines):
        self = cls('')

        # Decode the header and remove it from the lines
        tokens = lines[0].rstrip().split('F')
        if len(tokens) == 2 and tokens[1]:
            self.stack_patch = StackPatch.read(tokens[1])
        del lines[0]

        # These lines consist of different patches, each with a header. We will iterate over the headers and
        # read in the lines associated with them.
        offset = -1
        idx = 0
        while idx < len(lines):
            # Get the header, strip the line, removing newline and such
            header = lines[idx].rstrip()

            # Get the location of the identifying uppercase, and the relative offset
            # If there relative offset is encoded, it was 0.
            up_idx = support.find_first_uppercase(header)
            offset += hex_int(header[:up_idx]) +1 if (up_idx != 0) else 1

            # Handle the right type of patch
            idx += 1 # Move to the line after the header, easier indexing after this
            for patch_type in (AdditionPatch, DeletionPatch, LinePatch, SubstitutionPatch):
                (size, patch) = patch_type.read(offset, header[up_idx:], lines[idx:])
                if patch:
                    self.patches.append(patch)
                    break

            # Go to the next header. This header has already been skipped, so skip the extra lines (size)
            idx += size

        return self

    # Update the address offset to take alignment into account
    @staticmethod
    def update_address_offset(alignment):
        global address_offset
        address_offset = support.align(address_offset, alignment)
    
class PatchFile:
    """A class representing a patch"""
    def __init__(self):
        self.func_patches = []

    def __repr__(self):
        res = ''
        for func in self.func_patches:
            res = res + repr(func)
        return res

    def __str__(self):
        res = ''
        prev_idx = -1
        for (idx, func) in enumerate(self.func_patches):
            patch = str(func)
            # We won't output empty patches. We simply prepend an offset to every function patch
            # that represents the number of empty patches that went before. If the offset is 0,
            # don't encode it.
            if patch != '\n':
                offset = idx - prev_idx -1
                if offset:
                    res += hex_str(offset)
                res += 'F' + patch
                prev_idx = idx
        return res

    def apply(self, symfile):
        self.init_address_offset()

        # If we're missing patches for the last N functions, simply create empty patches for them
        for (func, patch) in itertools.zip_longest(symfile.funcs, self.func_patches, fillvalue=FuncPatch('')):
            patch.apply(func)

    # The constructor to create a PatchFile from two symfiles
    @classmethod
    def create(cls, base, div):
        self = cls()
        cls.init_address_offset()
        for (func_base, func_div) in zip(base.funcs, div.funcs):
            self.func_patches.append(FuncPatch.create(func_base, func_div))
        return self

    @staticmethod
    def init_address_offset():
        # The address offset we track during patch creation/application. We initialize this on 0 every time
        # a patchfile is created.
        global address_offset
        address_offset = 0

    # The constructor to create a PatchFile by reading it in from a file
    @classmethod
    def read(cls, path):
        self = cls()
        with open(path, 'r') as f:
            # Find all the function patches and determine how many empty patches there are between them
            patch_lines = []
            for line in f:
                if 'F' in line:
                    # If we were gathering lines for a patch (we won't be in the beginning), create it
                    if patch_lines:
                        self.func_patches.append(FuncPatch.read(patch_lines))

                    # Add this line (the patch header) to the lines
                    patch_lines = [line]

                    # Find out the offset. If none is encoded it was 0. With the offset we also know
                    # how many empty function patches there are and can create them
                    token_pos = line.find('F')
                    offset = hex_int(line[:token_pos]) if (token_pos != 0) else 0
                    for _ in range(offset):
                        self.func_patches.append(FuncPatch(''))

                else:
                    # Add this line for the patch we are preparing
                    patch_lines.append(line)

            # Finish last patch
            if patch_lines:
                self.func_patches.append(FuncPatch.read(patch_lines))

        return self

    def write(self, path, verbose=False):
        # Get the output and write it out. This can be more verbose (and better readable by humans) or minimally encoded (and better parsable)
        output = repr(self) if verbose else str(self)
        with open(path, 'w') as f:
            f.write(output)
