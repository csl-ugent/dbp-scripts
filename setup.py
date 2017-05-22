#!/usr/bin/python3
import os
import subprocess

# Import own modules
import config
import support

def main():
    # Generate the seeds to be used by the rest of the toolflow
    print('************ Generating seeds **********')
    support.generate_seeds(config.nr_of_measurements, config.root_seed)

    # Create the subdirectories
    print('************ Creating subdirectories **********')
    if not os.path.exists(config.tmp_dir):
        os.mkdir(config.tmp_dir)
    if not os.path.exists(config.reports_dir):
        os.mkdir(config.reports_dir)

    # Generate helper tools
    print('************ Making replay tools **********')
    subprocess.check_call(['make', 'all', 'LLVM_DIR=' + config.clang_dir], cwd=config.replay_dir)

    print('************ Making dump tools **********')
    subprocess.check_call(['make', 'all', 'CXX=' + config.gcc_bin, 'CPPFLAGS=' + config.binary_options + ' -I' + os.path.join(config.breakpad_dir, 'src')], cwd=config.dump_dir)

    print('************ Making breakpad tools **********')
    if not os.path.exists(config.breakpad_server_dir):
        os.mkdir(config.breakpad_server_dir)
        subprocess.check_call([os.path.join(config.breakpad_dir, 'configure')], cwd=config.breakpad_server_dir)
        subprocess.check_call(['make'], cwd=config.breakpad_server_dir)

if __name__ == '__main__':
    main()
