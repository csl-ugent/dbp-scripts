#!/usr/bin/python3
import argparse
import os
import shutil

# Import own modules
import config
import init
import build_binaries
import link_binaries
import extract_data
import create_patches
import inject_delta_data
import report_binary_sizes
import report_binary_text_sizes
import report_delta_data_sizes
import report_opportunity_log_sizes
import report_patch_sizes
import report_patch_timing
import report_symfile_sizes

def complete_run(args, report=True):
    # Run everything
    init.main()
    build_binaries.main(args)
    link_binaries.main()
    extract_data.main()
    create_patches.main()
    inject_delta_data.main(False)

    # Create reports
    if report:
        report_binary_sizes.main()
        report_binary_text_sizes.main()
        report_delta_data_sizes.main()
        report_opportunity_log_sizes.main()
        report_patch_sizes.main()
        report_patch_timing.main()
        report_symfile_sizes.main()

def generate_results(args, name):
    # Create output directory
    output_dir = os.path.join(config.base_dir, name)
    shutil.rmtree(output_dir, True)
    os.mkdir(output_dir)
    config.set_base_dir(output_dir)

    # Generate the results for these arguments
    complete_run(args)

if __name__ == '__main__':
    # Parsing the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--arguments', nargs=argparse.REMAINDER, help='The arguments with which to compile the benchmarks.')
    parser.add_argument('-r', '--report', action='store_true', help='Create reports.')
    args = parser.parse_args()

    # If there are specific compilation arguments, do a run simply for these. If not, generate all results.
    if args.arguments is not None:
        complete_run(args.arguments, args.report)
    else:
        for olevel in ['-O' + str(iii) for iii in list(range(1, 3 +1)) + ['s']]:
            generate_results([olevel, '-fomit-frame-pointer'], 'nofp_' + olevel)
            generate_results([olevel], 'fp_' + olevel)
