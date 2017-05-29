#!/usr/bin/python3
import concurrent.futures
import logging
import os

# Import own modules
import config
import delta_data
import support

def inject_data(benchmark, name, seeds, encrypt):
    try:
        # Determine all paths
        binary = os.path.join(support.create_path_for_seeds(config.build_dir, *seeds), benchmark, name)
        patch_dir = os.path.join(support.create_path_for_seeds(config.patches_dir, *seeds), benchmark)
        print('************ Injecting delta data for binary ' + binary + ' **********')

        # Get the patch
        with open(os.path.join(patch_dir, 'patch'), 'rb') as f_p:
            patch = f_p.read()

        # Encode the delta data and write it to a file
        dd = delta_data.encode(seeds, patch, encrypt)
        dd_path = os.path.join(patch_dir, 'delta_data')
        with open(dd_path, 'wb') as f_dd:
            f_dd.write(dd)

        # Do the actual injection
        delta_data.inject(binary, dd_path)

    except Exception:
        logging.getLogger().exception('Delta data injection failed for ' + binary)

def main(encrypt=True):
    # Inject the delta data for every binary
    print('************ Injecting delta data **********')
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for seed_tuple in support.seeds_gen():
            for subset in support.subsets_gen(seed_tuple, False):
                for (benchmark, name) in support.benchmarks_gen():
                    executor.submit(inject_data, benchmark, name, subset, encrypt)

if __name__ == '__main__':
    main()
