#!/usr/bin/python3
import os
import shutil
import subprocess

# Import own modules
import config
import seed
import stacktrace
import support

def get_stacktraces(spec_conf, symfile_path, benchmark, name, diablo_options, run_dir):
    # Create the directory in which we'll execute our regression test
    os.makedirs(run_dir)

    # Run the regression script for the binary and get its stdout
    output = subprocess.check_output([config.regression_script, '-c', spec_conf, '-o', diablo_options, '-T', run_dir,
        '-d', os.path.dirname(config.diablo_bin), '-p', os.path.basename(config.diablo_bin), name], stderr=subprocess.DEVNULL, universal_newlines=True)

    stacktraces = []
    for dump in stacktrace.get_dumps_for_output(output, benchmark, run_dir):
        # Set up the symbols directory for stackwalk
        symbols_dir = stacktrace.setup_symbols_dir_for_dump(dump, symfile_path, name, run_dir)

        # Use stackwalk to get the decoded stacktrace
        stacktraces.append(subprocess.check_output([config.minidump_stackwalk, dump, symbols_dir], stderr=subprocess.DEVNULL, universal_newlines=True))

    return stacktraces

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

def main():
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

if __name__ == '__main__':
    main()
