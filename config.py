import logging
import os
import sys

# Parameters
default_padding = 8
gpg_passphrase = 'breakpad_pass'
max_padding = 256
max_seed = 1000000
nr_of_measurements = 30
root_seed = 101
ssh_params = # You should put the parameters required to SSH to your testing board here (e.g. '-p 915 babrath@arndale')
target_triple =
cross_compilation_options =

# Non-configurable directories and files that are located inside this repository.
scripts_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
ld_dir = os.path.join(scripts_dir, 'ld')
dump_dir = os.path.join(scripts_dir, 'dump')
replay_src_dir = os.path.join(scripts_dir, 'replay')

# Configurable directories and files for the test directory. Setting base_dir
# should be enough, the rest is derived from it (but can be changed).
base_dir =
extra_build_dir = os.path.join(base_dir, 'extra_build') # This directory contains the build directories for extra source code (such as breakpad client)
breakpad_server_dir = os.path.join(base_dir, 'breakpad_server')
build_dir = os.path.join(base_dir, 'build')
data_dir = os.path.join(base_dir, 'data')
gpg_dir = os.path.join(base_dir, 'gpg')
log_file = os.path.join(base_dir, 'errors')
patches_dir = os.path.join(base_dir, 'patches')
replay_dir = os.path.join(base_dir, 'replay')
reports_dir = os.path.join(base_dir, 'reports')
results_dir = os.path.join(base_dir, 'results')
tmp_dir = os.path.join(base_dir, 'tmp')
link_script = os.path.join(tmp_dir, 'link.xc')
seed_file = os.path.join(base_dir, 'seeds.txt')
spec_dir = os.path.join(base_dir, 'spec2006')

# Error logging, log everything to the same file.
def init_logging():
    logger = logging.getLogger()
    fh = logging.FileHandler(log_file)
    logger.addHandler(fh)
init_logging()

# Paths for repositories/tools we use
breakpad_dir =
clang_dir =
cross_toolchain_dir =
regression_dir =
spec_tarball =

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
binary_options = '-fno-PIC -ffunction-sections -g ' + cross_compilation_options # These are general compile options for code that is to go into the protected binary
