#!/usr/bin/python3
import os
import shutil
import subprocess
import sys

# Import own modules
import config

# Start with destroying the previous directory structure, if it exists
shutil.rmtree(config.results_dir, True)
os.mkdir(config.results_dir)

def complete_run(args, name):
    # Run everything
    subprocess.check_call(['./setup.py'])
    subprocess.check_call(['./setup_sp.py'] + args)
    subprocess.check_call(['./setup_fs.py'])
    subprocess.check_call(['./setup_nop.py'])
    subprocess.check_call(['./extract_data.py'])
    subprocess.check_call(['./create_patches.py'])
    subprocess.check_call(['./report_binary_sizes.py'])
    subprocess.check_call(['./report_binary_text_sizes.py'])
    subprocess.check_call(['./report_opportunity_log_sizes.py'])
    subprocess.check_call(['./report_patch_sizes.py'])
    subprocess.check_call(['./report_symfile_sizes.py'])

    # Copy over the stuff we want (data, patches, reports, and errors)
    output_dir = os.path.join(config.results_dir, name)
    os.mkdir(output_dir)
    shutil.move(config.data_dir, output_dir)
    shutil.move(config.patches_dir, output_dir)
    shutil.move(config.reports_dir, output_dir)
    shutil.move(config.log_file, output_dir)

for olevel in ['-O' + str(iii) for iii in list(range(1, 3 +1)) + ['s']]:
    complete_run([olevel, '-fomit-frame-pointer'], 'nofp_' + olevel)
    complete_run([olevel], 'fp_' + olevel)
