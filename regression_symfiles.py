#!/usr/bin/python3
import os
import shutil
import subprocess

# Import own modules
import config
import seed
import support

def get_stacktraces(spec_conf, symfile_path, benchmark, name, diablo_options, run_dir):
    # Create the directory in which we'll execute our regression test
    os.makedirs(run_dir)

    # Run the regression script for the binary and get its stdout
    output = subprocess.check_output([config.regression_script, '-c', spec_conf, '-o', diablo_options, '-T', run_dir,
        '-d', os.path.dirname(config.diablo_bin), '-p', os.path.basename(config.diablo_bin), name], stderr=subprocess.DEVNULL, universal_newlines=True)

    stacktraces = []
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
        local_dump_path = os.path.join(run_dir, str(len(stacktraces)) + '.dmp')
        subprocess.check_call(['scp', config.ssh_params + ':' + dump_path, local_dump_path], stdout=subprocess.DEVNULL)

        # Use stackwalk to get the ID
        modules = False
        symfile_id = None
        for line in subprocess.check_output([config.minidump_stackwalk, local_dump_path], stderr=subprocess.DEVNULL, universal_newlines=True).splitlines():
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

        # Use stackwalk to get the decoded stacktrace
        stacktraces.append(subprocess.check_output([config.minidump_stackwalk, local_dump_path, symbols_dir], stderr=subprocess.DEVNULL, universal_newlines=True))

    return stacktraces

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

def regression_test(tmp_dir, benchmark, name, bkpt_seed):
    # We will put everything for this run in one directory
    run_dir = os.path.join(tmp_dir, str(bkpt_seed), benchmark)
    os.makedirs(run_dir)

    base_options = [config.diablo_options, '-bkpto', '-bkptos', str(bkpt_seed)]

    # Get the stacktraces for the binary without NOP insertion or flowgraphing. We don't flowgraph
    # as this results in the merging of text sections and a change in their base address.
    diablo_options = base_options + ['-F']
    base_symfile = os.path.join(support.create_path_for_seeds(config.data_dir), benchmark, 'symfile')
    base_st = get_stacktraces(spec_conf, base_symfile, benchmark, name, ' '.join(diablo_options), os.path.join(run_dir, 'base'))

    # No breakpoints were hit and no stacktraces were generated
    if not base_st:
        print('Normal execution for ' + name + ' seed: ' + str(bkpt_seed))
        return

    for nop_seed, in support.seeds_gen(seed.NOPSeed):
        # Get the stacktraces for the NOP inserted binary
        diablo_options = base_options + ['--nopinsertionchance', str(config.nop_chance), '--nopinsertionseed', str(nop_seed)]
        div_symfile = os.path.join(support.create_path_for_seeds(config.data_dir, nop_seed), benchmark, 'symfile')
        div_st = get_stacktraces(spec_conf, div_symfile, benchmark, name, ' '.join(diablo_options), os.path.join(run_dir, str(nop_seed)))

        # Compare the stacktraces
        for iii, (a, b) in enumerate(zip(base_st, div_st)):
            if not stacktraces_equal(a, b, name):
                print('Differing stacktraces for ' + name + ' nop_seed ' + str(nop_seed) + ' bkpt_seed ' + str(bkpt_seed))
                stacktrace_print(a, os.path.join(run_dir, str(iii) + 'st_base'))
                stacktrace_print(b, os.path.join(run_dir, str(iii) + 'st_' + str(nop_seed)))
            else:
                print('Identical stacktraces for ' + name + ' nop_seed ' + str(nop_seed) + ' bkpt_seed ' + str(bkpt_seed))

# The subdirectory within the tmp directory we'll use for our regression testing, clean it up from previous runs.
tmp_dir = os.path.join(config.tmp_dir, 'nop_test')
shutil.rmtree(tmp_dir, True)
os.makedirs(tmp_dir)

# We'll test only symfiles generated for NOP insertion on base binaries, for a maximum
# number of seeds.
spec_conf = os.path.join(support.create_path_for_seeds(config.build_dir), 'spec2006_test.conf')
max_seed = 9999

for bkpt_seed in range(1, max_seed):
    for (benchmark, name) in support.benchmarks_gen():
        regression_test(tmp_dir, benchmark, name, bkpt_seed)
