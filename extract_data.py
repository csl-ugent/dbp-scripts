#!/usr/bin/python3
import concurrent.futures
import logging
import os
import pickle
import shutil
import subprocess

# Import own modules
import config
import linker
import seed
import support
from symfile import SymFile

def extract_data(seed_tuple, subset, pickle_symfiles=False):
    try:
        # Unpack all the seeds we need and create the relative path
        (orig_sp_seed, orig_fs_seed) = support.get_seeds_from_tuple(seed_tuple, seed.SPSeed, seed.FSSeed)
        (sp_seed, fs_seed) = support.get_seeds_from_tuple(subset, seed.SPSeed, seed.FSSeed)
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

            # Copy over the opportunity logs
            if not sp_seed:
                shutil.copy2(os.path.join(support.create_path_for_seeds(config.build_dir, orig_sp_seed, fs_seed), benchmark, 'stackpadding.list'), data_dir)

            # If we're dealing with the base we have to do some more stuff
            if not subset:
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

        # Copy over the stackpadding list for the extra build archives/objects (these are the same for every benchmark)
        if not subset:
            shutil.copy2(os.path.join(support.create_path_for_seeds(config.extra_build_dir, orig_sp_seed), 'stackpadding.list'), os.path.join(config.data_dir, relpath))
    except Exception:
        logging.getLogger().exception('Data extraction failed for ' + relpath)

def main():
    # Start with destroying the previous directory structure, if it exists
    shutil.rmtree(config.data_dir, True)

    # Get the seeds and extract the data for the associated build
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for seed_tuple in support.all_seeds_gen():
            for subset in support.subsets_gen(seed_tuple, False):
                executor.submit(extract_data, seed_tuple, subset)

        executor.submit(extract_data, seed_tuple, ())

if __name__ == '__main__':
    main()
