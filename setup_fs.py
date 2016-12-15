#!/usr/bin/python3
import os
import random
import shlex
import subprocess

# Import own modules
import config
import linker
import seed
import support
from linker import Map

####################################################################################################
# Second diversification form - function shuffling.
# We prepare by copying the unshuffled binaries to the location where they'll be shuffled.
# Next we read in the linkermap for the benchmark and find all sections we need to create a linker
# script. We finish by creating a custom, shuffled linker script and re-executing the original
# link commands.
####################################################################################################

print('************ Preparing for function shuffling by copying binaries **********')
for sp_seed, fs_seed in support.seeds_gen(seed.SPSeed, seed.FSSeed):
    support.copy_spec_tree(support.create_path_for_seeds(config.build_dir), support.create_path_for_seeds(config.build_dir, fs_seed))
    support.copy_spec_tree(support.create_path_for_seeds(config.build_dir, sp_seed), support.create_path_for_seeds(config.build_dir, sp_seed, fs_seed))

for (benchmark, name) in support.benchmarks_gen():
    # Get all the sections from all the objects in the build directory
    print('************************* ' + benchmark + ' **********************')
    print('************************* Gathering sections **********************')
    linkermap = Map(os.path.join(support.create_path_for_seeds(config.build_dir), benchmark, name + '.map'))

    # Get all the pre_sections and make linker rules out of them. We do this so that they can't change order (which apparently, they can...).
    # Use a '*' (even though it is unnecessary) so Diablo's map parser will recognize it as a pattern.
    # Remove the name of the encompassing archive from an object (if it exists), else Diablo can't handle this
    pre_sections = [[support.get_objname(section.obj) + '*(' + section.name + ')'] for section in linkermap.pre_sections]

    # We want to create a list of all linker rules to be shuffled. Ideally we would simply take all sections currently in the
    # linkermap (that we want to shuffle) and convert them into a rule that matches only that section from its specific object.
    # Unfortunately the linker is a bit fickle in its handling of weak symbols. If N sections (coming from N different objects)
    # exist that define the same symbol, the linker will select only one (from one object) to place in the binary and discard
    # the rest. The problem is that during the second, function-shuffling link (using the linker script we generate here) the
    # linker won't necessarily select a weak symbol section from the same object as it did in the first link. The custom rule
    # (which includes the name of the object the section came from the first link) won't match and the section would be put
    # after the sections that ARE shuffled. To avoid this, we also keep all discarded sections, and then create N rules for the
    # section (one for each object). These rules stay together during shuffling, thus guaranteeing the right location of the section.
    shuffle_sections = []
    for section in linkermap.shuffle_sections:
        rule_list = []

        # Create the linker rules and insert them in the list
        # Use a '*' (even though it is unnecessary) so Diablo's map parser will recognize it as a pattern.
        # Remove the name of the encompassing archive from an object (if it exists), else Diablo can't handle this
        suffix = '*(' + section.name + ')'
        rule_list.append(support.get_objname(section.obj) + suffix)
        for discarded in linkermap.discarded_sections:
            if discarded.name == section.name:
                rule_list.append(support.get_objname(discarded.obj) + suffix)

        # Add the rule list to the list of lists
        shuffle_sections.append(rule_list)

    # Do the actual function shuffling by creating a new linker script (with shuffled sections) and relinking
    for sp_seed, fs_seed in support.seeds_gen(seed.SPSeed, seed.FSSeed):
        print('************************* Shuffling for ' + str(fs_seed) + ' **********************')

        # Shuffle the section array, make sure to convert the seed to INT before seeding!
        # Also copy the list (shuffle to shuffleD, so that every time we start shuffling from the original array)
        random.seed(fs_seed)
        shuffled_sections = list(shuffle_sections)
        random.shuffle(shuffled_sections)

        # Create diversified link script
        linker.create_linker_script(pre_sections + shuffled_sections)

        # Get the link commands. These don't have to be adapted as the command already contains a linker script.
        dir_no = os.path.join(support.create_path_for_seeds(config.build_dir, fs_seed), benchmark)
        dir_sp = os.path.join(support.create_path_for_seeds(config.build_dir, sp_seed, fs_seed), benchmark)
        with open(os.path.join(dir_no, 'make.out'), 'r') as f:
            cmd_no = list(f)[-1].rstrip()
        with open(os.path.join(dir_sp, 'make.out'), 'r') as f:
            cmd_sp = list(f)[-1].rstrip()

        # Execute them with our diversified link script
        subprocess.check_call(shlex.split(cmd_no), cwd=dir_no)
        subprocess.check_call(shlex.split(cmd_sp), cwd=dir_sp)
