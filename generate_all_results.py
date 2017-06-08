#!/usr/bin/python3
import os
import shutil

# Import own modules
import config
import setup
import setup_sp
import setup_fs
import setup_nop
import extract_data
import create_patches
import report_binary_sizes
import report_binary_text_sizes
import report_opportunity_log_sizes
import report_patch_sizes
import report_patch_timing
import report_symfile_sizes

def complete_run(args, name):
    # Run everything
    config.init_logging()
    setup.main()
    setup_sp.main(args)
    setup_fs.main()
    setup_nop.main()
    extract_data.main()
    create_patches.main()
    report_binary_sizes.main()
    report_binary_text_sizes.main()
    report_opportunity_log_sizes.main()
    report_patch_sizes.main()
    report_patch_timing.main()
    report_symfile_sizes.main()

    # Copy over the stuff we want (data, patches, reports, and errors)
    output_dir = os.path.join(config.results_dir, name)
    os.mkdir(output_dir)
    shutil.move(config.data_dir, output_dir)
    shutil.move(config.patches_dir, output_dir)
    shutil.move(config.reports_dir, output_dir)
    shutil.move(config.log_file, output_dir)

def main():
    # Start with destroying the previous directory structure, if it exists
    shutil.rmtree(config.results_dir, True)
    os.mkdir(config.results_dir)

    for olevel in ['-O' + str(iii) for iii in list(range(1, 3 +1)) + ['s']]:
        complete_run([olevel, '-fomit-frame-pointer'], 'nofp_' + olevel)
        complete_run([olevel], 'fp_' + olevel)

if __name__ == '__main__':
    main()
