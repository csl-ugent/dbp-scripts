#!/usr/bin/python3
import os

# Import own modules
import config
import support

def main():
    print('************ Initialize logging  **********')
    config.init_logging(False)

    # Generate the seeds to be used by the rest of the toolflow
    print('************ Generating seeds **********')
    support.generate_seeds(config.nr_of_measurements, config.root_seed)

    # Create the subdirectories
    print('************ Creating subdirectories **********')
    if not os.path.exists(config.reports_dir):
        os.mkdir(config.reports_dir)
    if not os.path.exists(config.tmp_dir):
        os.mkdir(config.tmp_dir)

if __name__ == '__main__':
    main()
