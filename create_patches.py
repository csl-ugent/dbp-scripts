#!/usr/bin/python3
import concurrent.futures
import logging
import os
import shutil
import sys

# Import own modules
import config
import patch
import support

def create_patch(benchmark, seeds):
    try:
        # Determine all paths
        base_data = os.path.join(support.create_path_for_seeds(config.data_dir), benchmark)
        div_symfile_path = os.path.join(support.create_path_for_seeds(config.data_dir, *seeds), benchmark, 'symfile')
        patch_dir = os.path.join(support.create_path_for_seeds(config.patches_dir, *seeds), benchmark)
        print('************ Creating patch for benchmark ' + patch_dir + ' **********')

        # Make the subdirectories and create the patch
        os.makedirs(patch_dir)
        patch.patch(base_data, seeds, div_symfile_path=div_symfile_path, output_dir=patch_dir)

        # Verify the patch is correct
        if not patch.patch(base_data, seeds, div_symfile_path=div_symfile_path, patch_path=os.path.join(patch_dir, 'patch')):
            os.remove(os.path.join(patch_dir, 'patch'))
            os.remove(os.path.join(patch_dir, 'patch.bz2'))
            logging.getLogger().error('Patch verification failed for ' + patch_dir)
    except Exception:
        logging.getLogger().exception('Patch creation failed for ' + patch_dir)

# Start with destroying the previous directory structure, if it exists
shutil.rmtree(config.patches_dir, True)

# Create the patches by submitting tasks to the executor
print('************ Creating patches **********')
with concurrent.futures.ProcessPoolExecutor() as executor:
    for seed_tuple in support.seeds_gen():
        for subset in support.subsets_gen(seed_tuple, False):
            for (benchmark, _) in support.benchmarks_gen():
                executor.submit(create_patch, benchmark, subset)
