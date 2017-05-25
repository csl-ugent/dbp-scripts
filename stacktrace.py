import os
import subprocess

# Import own modules
import config

class StackFrame:
    """A class representing a stack frame"""
    def __init__(self, line):
        # Leave out the offset in hex (NOP insertion can cause differences here)
        self.location = line.split()[:-1]
        self.stack_scanning = False # We assume the frame wasn't found through stack scanning until proven otherwise

# Get all the lines containing source line information
def get_frames(st, name):
    frames = []
    for line in st.splitlines():
        if name + '!' in line:
            frames.append(StackFrame(line))
            continue

        if 'Found by: stack scanning' in line:
            frames[-1].stack_scanning = True
            continue

    return frames

def stacktraces_equal(st_a, st_b, name):
    for f_a, f_b in zip(get_frames(st_a, name), get_frames(st_b, name)):
        if f_a.location != f_b.location:
            # When the frames differ but one of them was found through stack scanning (which can be unreliable) we'll return True.
            # This is because we don't trust the stack scanning and thus consider this as potentially a false positive. If no stack
            # scanning was used we'll of course return False.
            if f_a.stack_scanning or f_b.stack_scanning:
                return True
            else:
                return False

    return True

def stacktrace_print(st, path):
    with open(path, 'w') as f:
        f.write(st)

# Set up the symbols directory so that it contains the right symfile in the right directory subdirectory structure
def setup_symbols_dir_for_dump(dump, symfile_path, name, run_dir):
    # Use stackwalk to get the symfile ID
    modules = False
    symfile_id = None
    for line in subprocess.check_output([config.minidump_stackwalk, dump], stderr=subprocess.DEVNULL, universal_newlines=True).splitlines():
        if line == 'Loaded modules:':
            modules = True
            continue

        if modules and name in line:
            tokens = line.split()
            symfile_id = tokens[-1][:-1]

    assert symfile_id, 'Couldn\'t extract the symfile ID from the minidump!'

    # Set up the directory structure so the right symbol file is found
    symbols_dir = os.path.join(run_dir, 'symbols')
    symfile_dir = os.path.join(symbols_dir, name, symfile_id)
    if not os.path.exists(symbols_dir):
        os.makedirs(symfile_dir)
        os.symlink(symfile_path, os.path.join(symfile_dir, name + '.sym'))

    return symbols_dir


# This function filters the output from the regression script to find and download the minidumps produced.
def get_dumps_for_output(output, benchmark, run_dir):
    dumps = []
    for line in output.splitlines():
        # We get the name of the error file by looking for the redirection of stderr preceding it
        tokens = line.split()
        if '2>>' in tokens:
            err_idx = tokens.index('2>>') +1
            err_file = tokens[err_idx]
        else:
            continue

        # If the error file wasn't downloaded (happens for soplex), do it now
        err_file_path = os.path.join(run_dir, err_file)
        if not os.path.exists(err_file_path):
            subprocess.check_call(['scp', config.ssh_params + ':~/' + benchmark + '/' + err_file, err_file_path], stdout=subprocess.DEVNULL)

        # Get the path of the dump
        dump_path = None
        with open(err_file_path, 'r') as f:
            for line in f:
                tokens = line.split()
                if tokens[0] == 'DBP_DUMP_PATH:':
                    dump_path = tokens[1]

        # If no dump path is present no breakpoint was triggered and no minidump is available (hopefully only for this run instead of all runs).
        if not dump_path:
            continue

        # Download the dump file
        local_dump_path = os.path.join(run_dir, str(len(dumps)) + '.dmp')
        subprocess.check_call(['scp', config.ssh_params + ':' + dump_path, local_dump_path], stdout=subprocess.DEVNULL)
        dumps.append(local_dump_path)

    return dumps
