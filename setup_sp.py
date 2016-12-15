#!/usr/bin/python3
import multiprocessing
import os
import shlex
import shutil
import subprocess
from string import Template

# Import own modules
import config
import linker
import seed
import support

####################################################################################################
# First diversification form - stackpadding. The benchmarks are compiled using the patched LLVM.
# We create templated commands to install SPEC and get the arguments. Then do the installation
# for the default case and all the stack padding seeds.
####################################################################################################

# Use the default template linker script to minimize the differences when we started using the shuffled one based on it
linker.create_linker_script(None)

# Clean up from possible previous runs
shutil.rmtree(config.build_dir, True)

# Some SPEC configuration
spec_config_name = 'spec2006'

install_cmd = Template('$binary $install_options -j $concurrency -D -d $spec_dir -c $spec_config_name -t $gcc_toolchain_dir -p $target_triple -C $clang_dir '
        '-O "${compile_options} -Wl,--no-demangle -Wl,--hash-style=sysv -Wl,--no-merge-exidx-entries -Wl,-T $link_script ${llvm_options}"')
install_dict = {
    'binary' : config.spec_install_script,
    'clang_dir': config.clang_dir,
    'compile_options': config.spec_options,
    'concurrency': multiprocessing.cpu_count() -1,
    'gcc_toolchain_dir': config.gcc_toolchain_dir,
    'target_triple': config.target_triple,
    'install_options': '',
    'link_script': config.link_script,
    'llvm_options': '',
    'spec_config_name': 'base',
    'spec_dir': config.spec_dir
}

s2r_cmd = Template('$binary -s "${ssh_params}" -p $spec_dir -b build_base_${spec_config_name}-nn.0000 -d $target_dir')
s2r_dict = {
    'binary' : config.spec2regression_script,
    'spec_dir': config.spec_dir,
    'spec_config_name': spec_config_name,
    'ssh_params': config.ssh_params,
    'target_dir': support.create_path_for_seeds(config.build_dir)
}

# Install SPEC if necessary
if not os.path.exists(config.spec_dir):
    subprocess.check_call(shlex.split(install_cmd.substitute(install_dict)))

# Start by compiling for the default binaries
print('************ Building default binaries... **********')
install_dict['install_options'] = '-r'
install_dict['llvm_options'] = '-mllvm -stackpadding=' + str(config.default_padding)
install_dict['spec_config_name'] = spec_config_name
subprocess.check_call(shlex.split(install_cmd.substitute(install_dict)))
subprocess.check_call(shlex.split(s2r_cmd.substitute(s2r_dict)))
print('************ Build finished. **********')

# Then compile for diversfied binaries (stackpadding only)
for sp_seed, in support.seeds_gen(seed.SPSeed):
    print('************ Building stackpadded binary for seed ' + str(sp_seed) + '... **********')
    # Adapt the arguments so that now we use the real max padding and add random padding
    install_dict['llvm_options'] = '-mllvm -stackpadding=' + str(config.max_padding) + ' -mllvm -padseed=' + str(sp_seed)
    s2r_dict['target_dir'] = support.create_path_for_seeds(config.build_dir, sp_seed)
    subprocess.check_call(shlex.split(install_cmd.substitute(install_dict)))
    subprocess.check_call(shlex.split(s2r_cmd.substitute(s2r_dict)))
    print('************ Build finished. **********')
