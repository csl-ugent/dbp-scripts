import logging
import os
import sys

# Parameters
default_padding = 8
gpg_passphrase = 'breakpad_pass'
max_padding = 256
max_seed = 1000000
nopinsertion_chance = 20
nr_of_measurements = 30
root_seed = 101
ssh_params = 'arndale' # You should put the parameters required to SSH to your testing board here (e.g. '-p 915 babrath@arndale')
target_triple = 'arm-linux-gnueabihf'
cross_compilation_options = '-target ' + target_triple + ' -mcpu=cortex-a8 -marm -I /usr/arm-linux-gnueabihf/include/c++/4.9.3/ -I /usr/arm-linux-gnueabihf/include/c++/4.9.3/backward -I /usr/arm-linux-gnueabihf/include/c++/4.9.3/arm-linux-gnueabihf/ -I /usr/arm-linux-gnueabihf/include/'

# Non-configurable directories and files that are located inside this repository.
scripts_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
ld_dir = os.path.join(scripts_dir, 'ld')
dump_dir = os.path.join(scripts_dir, 'dump')
replay_src_dir = os.path.join(scripts_dir, 'replay')

# Configurable directories for helper tools and such that only need to be set up once.
# Setting bin_dir should be enough.
bin_dir = '/opt/bin'
breakpad_server_dir = os.path.join(bin_dir, 'breakpad_server')
gpg_dir = os.path.join(bin_dir, 'gpg')
replay_dir = os.path.join(bin_dir, 'replay')
spec_dir = os.path.join(bin_dir, 'spec2006')

# Configurable directories and files for base directory in which all results are generated.
# Setting base_dir should be enough. These variables can be re-configured by calling the
# set_base_dir function (which doesn't actually set base_dir itself, so that remains constant).
base_dir = '/opt/data'
def set_base_dir(base_dir):
    global build_dir, data_dir, extra_build_dir, log_file, patches_dir, reports_dir, seed_file, tmp_dir, link_script
    build_dir = os.path.join(base_dir, 'build')
    data_dir = os.path.join(base_dir, 'data')
    extra_build_dir = os.path.join(base_dir, 'extra_build') # This directory contains the build directories for extra source code (such as breakpad client)
    log_file = os.path.join(base_dir, 'errors')
    patches_dir = os.path.join(base_dir, 'patches')
    reports_dir = os.path.join(base_dir, 'reports')
    seed_file = os.path.join(base_dir, 'seeds.txt')
    tmp_dir = os.path.join(base_dir, 'tmp')
    link_script = os.path.join(tmp_dir, 'link.xc')
set_base_dir(base_dir)

# Error logging, log everything to the same file.
def init_logging(append=True):
    logger = logging.getLogger()
    fh = logging.FileHandler(log_file, mode='a' if append else 'w')
    logger.addHandler(fh)
if os.path.exists(base_dir):
    init_logging()

# Paths for repositories/tools we use
breakpad_dir = '/opt/breakpad/src'
clang_dir = '/opt/llvm'
cross_toolchain_dir = '/usr'
regression_dir = '/opt/regression/'
spec_tarball = '/opt/SPEC_CPU2006v1.1.tar.bz2'

# Paths for tools present in those repositories
breakpad_archive = os.path.join('src', 'client', 'linux', 'libbreakpad_client.a')
clang_bin = os.path.join(clang_dir, 'bin', 'clang')
dump_syms = os.path.join(breakpad_server_dir, 'src', 'tools', 'linux', 'dump_syms', 'dump_syms')
fake_diablo_bin = 'fakediablo.sh'
fake_diablo_dir = os.path.join(regression_dir, 'common', 'fakediablo')
minidump_stackwalk = os.path.join(breakpad_server_dir, 'src', 'processor', 'minidump_stackwalk')
regression_script = os.path.join(regression_dir, 'common', 'regression-main', 'regression.py')
spec_install_script = os.path.join(regression_dir, 'speccpu2006', 'install.sh')
spec2regression_script = os.path.join(regression_dir, 'speccpu2006', 'spec2regression.sh')

# Compilation options
breakpad_options = '-Wl,--library=stdc++ -Wl,--library=atomic -Wl,--library=pthread' # The options required to link with the breakpad client
binary_options = '-fno-PIC -ffunction-sections -gdwarf-3 ' + cross_compilation_options # These are general compile options for code that is to go into the protected binary
