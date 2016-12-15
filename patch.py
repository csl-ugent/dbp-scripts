#!/usr/bin/python3
import argparse
import os
import sys

# Import own modules
import replay
import seed
import support
from linker import Map
from patchfile import PatchFile
from support import seed_tuple
from symfile import SymFile

# The core of this script: We replay those protections we can, and create/apply a patch for what is left.
def core(base_data, div_path, seeds, patchfile):
    # Get the base symfile and augment the symfile with information from linker.
    base_symfile = SymFile().read_f(os.path.join(base_data, 'symfile'))
    linkermap = Map(os.path.join(base_data, 'map'), os.path.join(base_data, 'sections'))
    base_symfile.augment(linkermap, os.readlink(os.path.join(base_data, 'build')))

    ####################################################################################################
    # Replay the different protections for which we have the seed.
    ####################################################################################################
    (sp_seed, fs_seed, nop_seed) = support.get_seeds_from_tuple(seeds, seed.SPSeed, seed.FSSeed, seed.NOPSeed)

    if sp_seed:
        print('************ Replaying stack padding. **********')
        replay.replay_sp(base_symfile, sp_seed, base_data)

    if fs_seed:
        print('************ Replaying function shuffling. **********')
        replay.replay_fs(base_symfile, fs_seed)

    if nop_seed:
        print('************ Replaying NOP insertion. **********')
        replay.replay_nop(base_symfile, nop_seed, base_data)

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

def main():
    # Parsing the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--base_data', required=True, help='The directory containing the base data.')
    parser.add_argument('-s', '--seeds', required=True, type=seed_tuple, help='The seed.')
    parser.add_argument('-d', '--diversified_symfile', help='The path to the diversified symfile.')
    parser.add_argument('-p', '--patch', help='The path to the patch.')
    parser.add_argument('-o', '--output_directory', help='The directory where outputs will be written.')
    args = parser.parse_args()

    # Determine the mode of operation. If we are given a patch we should test it, if not we should generate one.
    if args.patch:
        if args.diversified_symfile:
            print('************ Patch validation mode. **********')

            # Apply the patch to the base_symfile and compare the (diversified) result with the diversified symfile
            patched_symfile = core(args.base_data, args.diversified_symfile, args.seeds, args.patch)
            div_symfile = SymFile().read_f(args.diversified_symfile)

            if patched_symfile == div_symfile:
                print('************ Patch verified. **********')
            else:
                print('************ Patch failed. **********')

        else:
            print('************ Patch application mode. **********')
            assert args.output_directory, 'Need an output directory to generate the symfile!'

            # Apply the patch to the base symfile and write out the patched (diversified) symfile
            patched_symfile = core(args.base_data, args.diversified_symfile, args.seeds, args.patch)
            patched_symfile.write().write_f(os.path.join(args.output_directory, 'symfile'))
            print('************ Patch applied. **********')

    else:
        assert args.diversified_symfile, 'No patch nor diversified symfile was given! There is nothing to do for this script!'

        print('************ Patch generation mode. **********')
        assert args.output_directory, 'Need an output directory to generate the patch!'

        # Generate the actual patch
        patch = core(args.base_data, args.diversified_symfile, args.seeds, args.patch)
        patch.write(os.path.join(args.output_directory, 'patch'))
        print('************ Patch generated. **********')

