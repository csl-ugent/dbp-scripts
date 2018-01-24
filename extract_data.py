#!/usr/bin/python3
import concurrent.futures
import logging
import os
import pickle
import shutil
import seed
import subprocess

# Import own modules
import config
import linker
import support
from symfile import SymFile

def extract_data(subset, pickle_symfiles=False):
    try:
        # Unpack all the seeds we need and create the relative path
        relpath = support.relpath_for_seeds(*subset)

        print('************ Extracting for path ' + relpath + ' **********')
        for (benchmark, name) in support.benchmarks_gen():
            # Create the output directory for this benchmark
            build_dir = os.path.join(config.build_dir, relpath, benchmark)
            data_dir = os.path.join(config.data_dir, relpath, benchmark)
            os.makedirs(data_dir)
            os.symlink(build_dir, os.path.join(data_dir, 'build'))

            with open(os.path.join(data_dir, 'symfile'), 'w') as f_sym:
                # Extract the actual symfile using dump_syms. This tool creates a LOT of warnings so we redirect stderr to /dev/null
                subprocess.check_call([config.dump_syms, os.path.join(build_dir, name)], stdout=f_sym, stderr=subprocess.DEVNULL)

            # If we're dealing with the base we have to do some more stuff
            if not subset:
                # For every protection, copy over the opportunity log, if any
                for opportunity_log in [s.opportunity_log for s in seed.get_types() if s.opportunity_log]:
                    shutil.copy2(os.path.join(support.create_path_for_seeds(config.build_dir), benchmark, opportunity_log), data_dir)

                # Copy over the linker map
                shutil.copy2(os.path.join(build_dir, name + '.map'), os.path.join(data_dir, 'map'))

                # Extract the section alignment information
                linker.gather_section_alignment(os.path.join(build_dir, name + '.map'), os.path.join(data_dir, 'sections'))

                if pickle_symfiles:
                    # Get the symfile
                    symfile_path = os.path.join(os.path.join(data_dir, 'symfile'))
                    symfile = SymFile().read_f(symfile_path)

                    # Pickle it
                    with open(os.path.join(data_dir, 'pickled_symfile'), 'wb') as f_pickle:
                        pickle.dump(symfile, f_pickle)

        if not subset:
            data_dir = os.path.join(config.data_dir, relpath)
            # For every protection, copy over the opportunity logs for the extra build archives/objects (which are the same for every benchmark), if any.
            # Also copy over the build_prefix (in symlink form).
            for a in os.listdir(support.create_path_for_seeds(config.extra_build_dir)):
                a_path = os.path.join(support.create_path_for_seeds(config.extra_build_dir), a)
                os.symlink(os.readlink(os.path.join(a_path, 'build')), os.path.join(data_dir, 'build.' + a))
                for opportunity_log in [s.opportunity_log for s in seed.get_types() if s.opportunity_log]:
                    shutil.copy2(os.path.join(a_path, opportunity_log), os.path.join(data_dir, opportunity_log + '.' + a))

    except Exception:
        logging.getLogger().exception('Data extraction failed for ' + relpath)

def main():
    # Start with destroying the previous directory structure, if it exists
    shutil.rmtree(config.data_dir, True)

    # Get the seeds and extract the data for the associated build
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for seed_tuple in support.all_seeds_gen():
            for subset in support.subsets_gen(seed_tuple, False):
                executor.submit(extract_data, subset)

        executor.submit(extract_data, ())

if __name__ == '__main__':
    main()
