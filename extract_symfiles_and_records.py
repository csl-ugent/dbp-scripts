#!/usr/bin/python
import os
import shutil
import sys

# Import own modules
import config
import support

def extract_data(relpath, extract_records=False):
    for (benchmark, name) in support.benchmarks_gen():
        # Create the output directory for this benchmark
        output_dir = os.path.join(config.symfiles_dir, relpath, benchmark)
        symfile = os.path.join(output_dir, 'symfile')
        os.makedirs(output_dir)

        # Extract the actual symfile using dump_syms. This tool creates a LOT of warnings so we redirect stderr to /dev/null
        os.system(config.dump_syms + ' ' + os.path.join(config.build_dir, relpath, benchmark, name) + ' > ' + symfile + ' 2> /dev/null')

        # Only extract the records from the symfiles if explicitly requested
        if not extract_records: continue

        # Create the records files from the symfile
        os.system('grep MODULE ' + symfile + ' > ' + os.path.join(output_dir, 'MODULE_RECORD'))
        os.system('grep STACK ' + symfile + ' | sed "s/STACK CFI //"\ > ' + os.path.join(output_dir, 'STACK_RECORD'))
        os.system('grep PUBLIC ' + symfile + ' > ' + os.path.join(output_dir, 'PUBLIC_RECORD'))
        os.system('grep -v "MODULE\\|FILE\\|STACK\\|PUBLIC" ' + symfile + ' > ' + os.path.join(output_dir, 'FUNC_RECORD'))

        # Split up the FUNC_RECORD by function
        func_split_dir = os.path.join(output_dir, 'FUNC_SPLIT/')
        os.makedirs(func_split_dir)
        os.system('csplit --quiet --suffix-format %d --prefix ' + func_split_dir + ' ' + os.path.join(output_dir, 'FUNC_RECORD') + ' /FUNC/ "{*}"')

        # Select the columns we want from all these split files
        format_split_dir = os.path.join(output_dir, 'FUNC_FORMATTED_SPLIT')
        os.makedirs(format_split_dir)
        for f in os.listdir(func_split_dir):
            os.system('cut -d " " -f 2,3,4 ' + os.path.join(func_split_dir, f) + ' > ' + os.path.join(format_split_dir, f))

def diffing_data(base_relpath, div_relpath):
    for (benchmark, name) in support.benchmarks_gen():
        # Get the paths
        path_base = os.path.join(config.symfiles_dir, base_relpath, benchmark)
        path_div = os.path.join(config.symfiles_dir, div_relpath, benchmark)
        func_format_base = os.path.join(path_base, 'FUNC_FORMATTED_SPLIT')
        func_format_div  = os.path.join(path_div, 'FUNC_FORMATTED_SPLIT')

        # Make the output directory
        output_dir = os.path.join(path_div, 'DIFF_PER_FUNC')
        os.makedirs(output_dir)
        
        for f in os.listdir(func_format_base):
            diff1 = 'tail -n +2 ' + os.path.join(func_format_base, f)
            diff2 = 'tail -n +2 ' + os.path.join(func_format_div, f)
            os.system('bash -c \'diff <(' + diff1 + ') <(' + diff2 + ') | grep -v ">\|<\|---" > ' + os.path.join(output_dir, f) + '\'')

# Start with destroying the previous directory structure, if it exists
if os.path.exists(config.symfiles_dir):
    shutil.rmtree(config.symfiles_dir)

# Get the seeds and extract the data for the associated build
print('************ Extracting for the default **********')
extract_data(support.relpath_for_seeds())
for (sp_seed, fs_seed, nop_seed) in support.seeds_gen():
    print('************ Extracting for fs_seed ' + fs_seed + ' **********')
    extract_data(support.relpath_for_seeds(fs_seed=fs_seed), True)
    print('************ Extracting for sp_seed ' + sp_seed + ' **********')
    extract_data(support.relpath_for_seeds(sp_seed=sp_seed))
    print('************ Extracting for sp_seed ' + sp_seed + ', fs_seed ' + fs_seed + ' **********')
    extract_data(support.relpath_for_seeds(sp_seed=sp_seed, fs_seed=fs_seed), True)
    print('************ Diffing for sp_seed ' + sp_seed + ', fs_seed ' + fs_seed + ' **********')
    diffing_data(support.relpath_for_seeds(fs_seed=fs_seed), support.relpath_for_seeds(sp_seed=sp_seed, fs_seed=fs_seed))
