#!/usr/bin/python3
import argparse
import os
import pickle
import sys

# Import own modules
import support
from linker import Map
from patchfile import PatchFile
from support import seed_tuple
from symfile import SymFile

# The core of this script: We replay those protections we can, and create/apply a patch for what is left.
def core(base_data, div_path, seeds, patchfile):
    # Get the base symfile from a pickled version if it exists, or simply read it in
    pickled_symfile = os.path.join(base_data, 'pickled_symfile')
    if os.path.exists(pickled_symfile):
        with open(pickled_symfile, 'rb') as f:
            base_symfile = pickle.load(f)
    else:
        base_symfile = SymFile().read_f(os.path.join(base_data, 'symfile'))

    # Augment the symfile with information from linker.
    linkermap = Map(os.path.join(base_data, 'map'), os.path.join(base_data, 'sections'))
    base_symfile.augment(linkermap, os.readlink(os.path.join(base_data, 'build')))

    ####################################################################################################
    # Replay the different protections for which we have the seed.
    ####################################################################################################
    for seed in [seed for seed in seeds if seed]:
        seed.replay(base_symfile, base_data)

    ####################################################################################################
    # Handle the patch part: either we have a patch to apply, or we have to create one.
    ####################################################################################################
    if patchfile:
        print('************ Applying patch to symfile. **********')
        input_patch = PatchFile.read(patchfile)
        input_patch.apply(base_symfile)
    else:
        print('************ Creating patch from symfiles. **********')
        div_symfile = SymFile().read_f(div_path)
        output_patch = PatchFile.create(base_symfile, div_symfile)

    # If we had a patch to apply, return the resulting symfile. Else return the patch we created.
    return base_symfile if patchfile else output_patch

# This function checks the arguments. It exists so that the script's functionality can be invoked both from the command line as
# from another python script.
def patch(base_data, seeds, div_symfile_path=None, patch_path=None, output_dir=None, verbose=False):
    base_data = base_data.rstrip('/')

    # Determine the mode of operation. If we are given a patch we should test it, if not we should generate one.
    if patch_path:
        if div_symfile_path:
            print('************ Patch validation mode. **********')

            # Apply the patch to the base_symfile and compare the (diversified) result with the diversified symfile
            patched_symfile = core(base_data, None, seeds, patch_path)
            div_symfile = SymFile().read_f(div_symfile_path)

            if patched_symfile == div_symfile:
                print('************ Patch verified. **********')
            else:
                print('************ Patch failed. **********')
                return False

        else:
            print('************ Patch application mode. **********')
            assert output_dir, 'Need an output directory to generate the symfile!'

            # Apply the patch to the base symfile and write out the patched (diversified) symfile
            patched_symfile = core(base_data, None, seeds, patch_path)
            patched_symfile.write_f(os.path.join(output_dir, 'symfile'))
            print('************ Patch applied. **********')

    else:
        assert div_symfile_path, 'No patch nor diversified symfile was given! There is nothing to do for this script!'

        print('************ Patch generation mode. **********')
        assert output_dir, 'Need an output directory to generate the patch!'

        # Generate the actual patch
        patch = core(base_data, div_symfile_path, seeds, None)
        patch.write(os.path.join(output_dir, 'patch'), verbose)
        print('************ Patch generated. **********')

    return True

if __name__ == '__main__':
    # Parsing the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--base_data', required=True, help='The directory containing the base data.')
    parser.add_argument('-s', '--seeds', required=True, type=seed_tuple, help='The seed.')
    parser.add_argument('-d', '--diversified_symfile', help='The path to the diversified symfile.')
    parser.add_argument('-p', '--patch', help='The path to the patch.')
    parser.add_argument('-o', '--output_directory', help='The directory where outputs will be written.')
    parser.add_argument('-v', '--verbose', action='store_true', help='Create a verbose patch.')
    args = parser.parse_args()

    # Call the patch function and have a different exit value depending on its result
    res = patch(args.base_data, args.seeds, args.diversified_symfile, args.patch, args.output_directory, args.verbose)
    sys.exit(0 if res else 1)
