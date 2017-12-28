#!/usr/bin/python3
import os
import shlex
import subprocess

# Import own modules
import config
import linker
import seed
import support
from linker import Map

def main():
    # We prepare by copying the binaries to the location where they'll be protected
    print('************ Preparing for link-time protections by copying binaries **********')
    for link_protections in support.link_subsets_gen(seed.get_types(), False):
        for build_protections in support.build_subsets_gen(seed.get_types()):
            for build_seeds, link_seeds in zip(support.seeds_gen(*build_protections), support.seeds_gen(*link_protections)):
                support.copy_spec_tree(support.create_path_for_seeds(config.build_dir, *build_seeds), support.create_path_for_seeds(config.build_dir, *build_seeds, *link_seeds))

    for (benchmark, name) in support.benchmarks_gen():
        # Get all the sections from all the objects in the build directory
        print('************************* ' + benchmark + ' **********************')
        print('************************* Gathering sections **********************')
        linkermap = Map(os.path.join(support.create_path_for_seeds(config.build_dir), benchmark, name + '.map'))

        # Get all the pre_sections and make linker rules out of them. We do this so that they can't change order (which apparently, they can...).
        # Use a '*' (even though it is unnecessary) so Diablo's map parser will recognize it as a pattern.
        # Remove the name of the encompassing archive from an object (if it exists), else Diablo can't handle this
        pre_sections = [[support.get_objname(section.obj) + '*(' + section.name + ')'] for section in linkermap.pre_sections]

        # We want to create a list of all linker rules that can be altered. Ideally we would simply take all sections currently in the
        # linkermap (that we want to change) and convert them into a rule that matches only that section from its specific object.
        # Unfortunately the linker is a bit fickle in its handling of weak symbols. If N sections (coming from N different objects)
        # exist that define the same symbol, the linker will select only one (from one object) to place in the binary and discard
        # the rest. The problem is that during the second, protected link (using the linker script we generate here) the
        # linker won't necessarily select a weak symbol section from the same object as it did in the first link. The custom rule
        # (which includes the name of the object the section came from the first link) won't match and, for example, the section would
        # be put after the sections that ARE shuffled. To avoid this, we also keep all discarded sections, and then create N rules for the
        # section (one for each object). These rules stay together during the protections, thus guaranteeing the right location of the section.
        main_sections = []
        for section in linkermap.main_sections:
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
            main_sections.append(rule_list)

        # Perform the actual link-time protections by creating a new linker script (in which sections can change order) and relinking
        for link_protections in support.link_subsets_gen(seed.get_types(), False):
            # First create a new linker script for every combination of link protections
            for link_seeds in support.seeds_gen(*link_protections):
                print('************ Protecting binary at link level for ' + ' '.join([repr(s) for s in link_seeds]) + ' ... **********')

                # Copy the list so that every time we start from the original array
                protected_pre_sections = list(pre_sections)
                protected_main_sections = list(main_sections)
                for s in link_seeds:
                    protected_pre_sections, protected_main_sections = s.diversify_link(protected_pre_sections, protected_main_sections)

                # Create diversified link script
                linker.create_linker_script(protected_pre_sections + protected_main_sections, os.path.join(support.create_path_for_seeds(config.build_dir, *link_seeds), benchmark, 'link.xc'))


            for build_protections in support.build_subsets_gen(seed.get_types()):
                for build_seeds, link_seeds in zip(support.seeds_gen(*build_protections), support.seeds_gen(*link_protections)):
                    # Get the link command, then adapt it to use our new linker script
                    directory = os.path.join(support.create_path_for_seeds(config.build_dir, *build_seeds, *link_seeds), benchmark)
                    with open(os.path.join(directory, 'make.out'), 'r') as f:
                        cmd = list(f)[-1].rstrip()

                    new_script = os.path.join(support.create_path_for_seeds(config.build_dir, *link_seeds), benchmark, 'link.xc')
                    cmd = cmd.replace(config.link_script, new_script)

                    # Execute them with our diversified linker script
                    subprocess.check_call(shlex.split(cmd), cwd=directory)

if __name__ == '__main__':
    main()
