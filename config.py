#!/usr/bin/python3
import logging
import os
import sys

# Parameters
base_address = 0x8000
binary_options = '-ffunction-sections -g -mcpu=cortex-a8 -marm -O2' # These are general compile options for code that is to go into the protected binary
default_padding = 8
max_padding = 256
max_seed = 1000000
nop_chance = 20
nr_of_measurements = 30
root_seed = 101
ssh_params = # You should put the parameters required to SSH to your testing board here (e.g. '-p 915 babrath@arndale')
target_triple = 'arm-diablo-linux-gnueabi'

# Non-configurable directories and files that are located inside this repository.
scripts_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
ld_dir = os.path.join(scripts_dir, 'ld')
dump_dir = os.path.join(scripts_dir, 'dump')
replay_dir = os.path.join(scripts_dir, 'replay')

# Configurable directories and files for the test directory. Setting base_dir
# should be enough, the rest is derived from it (but can be changed).
base_dir =
extra_build_dir = os.path.join(base_dir, 'extra_build') # This directory contains the build directories for extra source code (such as breakpad client)
breakpad_server_dir = os.path.join(base_dir, 'breakpad_server')
build_dir = os.path.join(base_dir, 'build')
data_dir = os.path.join(base_dir, 'data')
log_file = os.path.join(base_dir, 'errors')
patches_dir = os.path.join(base_dir, 'patches')
reports_dir = os.path.join(base_dir, 'reports')
tmp_dir = os.path.join(base_dir, 'tmp')
link_script = os.path.join(tmp_dir, 'link.xc')
seed_file = os.path.join(base_dir, 'seeds.txt')
spec_dir = os.path.join(base_dir, 'spec2006')

# Error logging, log everything to the same file.
logger = logging.getLogger()
fh = logging.FileHandler(log_file)
logger.addHandler(fh)

# Paths for repositories/tools we use
breakpad_dir =
clang_dir =
diablo_bin =
gcc_toolchain_dir =
regression_dir =

# Paths for tools present in those repostories
breakpad_archive = os.path.join('src', 'client', 'linux', 'libbreakpad_client.a')
clang_bin = os.path.join(clang_dir, 'bin', 'clang')
dump_syms = os.path.join(breakpad_server_dir, 'src', 'tools', 'linux', 'dump_syms', 'dump_syms')
fake_diablo_bin = 'fakediablo.sh'
fake_diablo_dir = os.path.join(regression_dir, 'common', 'fakediablo')
gcc_bin = os.path.join(gcc_toolchain_dir, 'bin', target_triple + '-gcc')
strip_bin = os.path.join(gcc_toolchain_dir, 'bin', target_triple + '-strip')
minidump_stackwalk = os.path.join(breakpad_server_dir, 'src', 'processor', 'minidump_stackwalk')
regression_script = os.path.join(regression_dir, 'common', 'regression-main', 'regression.py')
spec_install_script = os.path.join(regression_dir, 'speccpu2006', 'install.sh')
spec2regression_script = os.path.join(regression_dir, 'speccpu2006', 'spec2regression.sh')

# Compiling options for tools
breakpad_options = '-Wl,--library=stdc++ -Wl,--library=atomic -Wl,--library=pthread -Wl,--library=:' + os.path.join(dump_dir, 'dump.o') # The options required to link with the breakpad client
clang_options = '-isysroot ' + os.path.join(gcc_toolchain_dir, target_triple, 'sysroot') + ' -no-integrated-as -gcc-toolchain ' + gcc_toolchain_dir + ' -ccc-gcc-name ' + target_triple + ' -target ' + target_triple # Extra options for clang, to make it use the gcc backend
diablo_options = '-Z -kco -exidx --no-merge-exidx'
