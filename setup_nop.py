#!/usr/bin/python3
import concurrent.futures
import logging
import os
import shlex
import subprocess
import sys

# Import own modules
import config
import seed
import support

####################################################################################################
# Third diversification form - NOP insertion. The benchmarks are rewritten by Diablo.
# For every Diablo run required, we determine the in- and output directories from the seeds,
# and then submit these as arguments for the run to the executor.
####################################################################################################

def run_diablo(name, nop_seed, input_dir, output_dir):
    try:
        print('************ Inserting NOPs for ' + input_dir + ' with nop_seed ' + str(nop_seed) + ' **********')

        # Run Diablo
        subprocess.check_call([config.diablo_bin, '-O', input_dir, '-o', name] + shlex.split(config.diablo_options) + ['--nopinsertionchance', str(config.nop_chance),
            '--nopinsertionseed', str(nop_seed), os.path.join(input_dir, name)], stdout=subprocess.DEVNULL, cwd=output_dir)
    except Exception:
        logging.getLogger().exception('NOP insertion failed for ' + input_dir + '/' + str(nop_seed))

def main():
    # Submitting Diablo runs as tasks to the executor
    print('************ Inserting NOPs using Diablo **********')
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for (sp_seed, fs_seed, nop_seed) in support.seeds_gen(seed.SPSeed, seed.FSSeed, seed.NOPSeed):
            for subset in support.subsets_gen((sp_seed, fs_seed)):
                # Clean up previous run and create directories
                support.copy_spec_tree(support.create_path_for_seeds(config.build_dir, *subset), support.create_path_for_seeds(config.build_dir, nop_seed, *subset))

                # Submit the Diablo runs
                for (benchmark, name) in support.benchmarks_gen():
                    input_dir = os.path.join(support.create_path_for_seeds(config.build_dir, *subset), benchmark)
                    output_dir = os.path.join(support.create_path_for_seeds(config.build_dir, nop_seed, *subset), benchmark)
                    executor.submit(run_diablo, name, nop_seed, input_dir, output_dir)

if __name__ == '__main__':
    main()
