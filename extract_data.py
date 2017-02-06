#!/usr/bin/python3
import concurrent.futures
import os
import shutil
import subprocess

# Import own modules
import config
import diablo_symfile
import linker
import seed
import support

def extract_data(seed_tuple, subset):
    # Unpack all the seeds we need and create the relative path
    (orig_sp_seed, orig_fs_seed, orig_nop_seed) = support.get_seeds_from_tuple(seed_tuple, seed.SPSeed, seed.FSSeed, seed.NOPSeed)
    (sp_seed, fs_seed, nop_seed) = support.get_seeds_from_tuple(subset, seed.SPSeed, seed.FSSeed, seed.NOPSeed)
    relpath = support.relpath_for_seeds(*subset)

    print('************ Extracting for path ' + relpath + ' **********')
    for (benchmark, name) in support.benchmarks_gen():
        # Create the output directory for this benchmark
        build_dir = os.path.join(config.build_dir, relpath, benchmark)
        data_dir = os.path.join(config.data_dir, relpath, benchmark)
        os.makedirs(data_dir)
        os.symlink(build_dir, os.path.join(data_dir, 'build'))

        with open(os.path.join(data_dir, 'symfile'), 'w') as f_sym:
            if nop_seed:
                no_nop_binary = os.path.join(support.create_path_for_seeds(config.build_dir, sp_seed, fs_seed), benchmark, name)
                listing = os.path.join(build_dir, name + '.list')
                diablo_symfile.create_updated_symfile(no_nop_binary, listing, f_sym)
            else:
                # Extract the actual symfile using dump_syms. This tool creates a LOT of warnings so we redirect stderr to /dev/null
                subprocess.check_call([config.dump_syms, os.path.join(build_dir, name)], stdout=f_sym, stderr=subprocess.DEVNULL)

        # Copy over the opportunity logs
        if not nop_seed:
            shutil.copy2(os.path.join(support.create_path_for_seeds(config.build_dir, sp_seed, fs_seed, orig_nop_seed), benchmark, 'nopinsertion.list'), data_dir)
        if not sp_seed:
            shutil.copy2(os.path.join(support.create_path_for_seeds(config.build_dir, orig_sp_seed, fs_seed), benchmark, 'stackpadding.list'), data_dir)

        # If we're dealing with the base we have to do some more stuff
        if not subset:
            # Copy over the linker map
            shutil.copy2(os.path.join(build_dir, name + '.map'), os.path.join(data_dir, 'map'))

            # Extract the section alignment information
            linker.gather_section_alignment(os.path.join(build_dir, name + '.map'), os.path.join(data_dir, 'sections'))

# Start with destroying the previous directory structure, if it exists
shutil.rmtree(config.data_dir, True)

# Get the seeds and extract the data for the associated build
with concurrent.futures.ProcessPoolExecutor() as executor:
    for seed_tuple in support.seeds_gen():
        for subset in support.subsets_gen(seed_tuple, False):
            executor.submit(extract_data, seed_tuple, subset)

    executor.submit(extract_data, seed_tuple, ())
