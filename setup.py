#!/usr/bin/python3
import gnupg
import multiprocessing
import os
import subprocess

# Import own modules
import config

def main():
    # Create the subdirectories
    print('************ Creating subdirectories **********')
    if not os.path.exists(config.tmp_dir):
        os.mkdir(config.tmp_dir)
    if not os.path.exists(config.gpg_dir):
        os.mkdir(config.gpg_dir, mode=0o700)

        print('************ Generate GPG key **********')
        gpg = gnupg.GPG(gnupghome=config.gpg_dir)
        key_settings = gpg.gen_key_input(key_type='RSA', key_length=2048, key_usage='encrypt', passphrase=config.gpg_passphrase)
        key = gpg.gen_key(key_settings)
        assert len(str(key)), 'GPG key was not successfully generated!'
        print(key)

    # Generate helper tools
    print('************ Making replay tools **********')
    subprocess.check_call(['make', 'all', 'LLVM_DIR=' + config.clang_dir], cwd=config.replay_dir)

    print('************ Making dump tools **********')
    subprocess.check_call(['make', 'all', 'CXX=' + config.clang_bin, 'CPPFLAGS=' + config.binary_options + ' -I' + os.path.join(config.breakpad_dir, 'src')], cwd=config.dump_dir)

    print('************ Making breakpad tools **********')
    if not os.path.exists(config.breakpad_server_dir):
        os.mkdir(config.breakpad_server_dir)
        subprocess.check_call([os.path.join(config.breakpad_dir, 'configure')], cwd=config.breakpad_server_dir)
        subprocess.check_call(['make'], cwd=config.breakpad_server_dir)

    # Install SPEC if necessary (this does not build any benchmarks)
    if not os.path.exists(config.spec_dir):
        subprocess.check_call([config.spec_install_script, '-j', str(multiprocessing.cpu_count()), '-i', '-d', config.spec_dir])

if __name__ == '__main__':
    main()
