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

install_cmd = Template('$binary -r -j $concurrency -D -d $spec_dir -c $spec_config_name -t $gcc_toolchain_dir -p $target_triple -C $clang_dir '
        '-O "${compile_options} -Wl,--no-demangle -Wl,--hash-style=sysv -Wl,--no-merge-exidx-entries -Wl,-T $link_script"')
install_dict = {
    'binary' : config.spec_install_script,
    'clang_dir': config.clang_dir,
    'compile_options': '',
    'concurrency': multiprocessing.cpu_count() -1,
    'gcc_toolchain_dir': config.gcc_toolchain_dir,
    'target_triple': config.target_triple,
    'link_script': config.link_script,
    'spec_config_name': '',
    'spec_dir': config.spec_dir
}

s2r_cmd = Template('$binary -s "${ssh_params}" -p $spec_dir -b build_base_${spec_config_name}-nn.0000 -t 5000 -d $target_dir')
s2r_dict = {
    'binary' : config.spec2regression_script,
    'spec_dir': config.spec_dir,
    'spec_config_name': '',
    'ssh_params': config.ssh_params,
    'target_dir': ''
}

# Builds all extra source code (such as the breakpad client archive) with the requested options. Returns the extra
# compile options that are required to link with the resulting objects/archives.
def build_extra(build_dir, compile_options):
    # Create the build directory (after cleaning up possible previous run)
    shutil.rmtree(build_dir, True)
    os.mkdir(build_dir)
    ret_options = [config.breakpad_options]

    # Build the breakpad archive
    print('************ Building breakpad archive **********')
    subprocess.check_call([os.path.join(config.breakpad_dir, 'configure'), '--host=arm-diablo-linux-gnueabi', '--disable-tools', '--disable-processor',
        'CC=' + config.clang_bin, 'CXX=' + config.clang_bin, 'CPPFLAGS=' + ' '.join(compile_options + [config.clang_options])], cwd=build_dir, stdout=subprocess.DEVNULL)
    subprocess.check_call(['make'], cwd=build_dir, stdout=subprocess.DEVNULL)
    ret_options.append('-Wl,--library=:' + os.path.join(build_dir, config.breakpad_archive))

    return ret_options

# Build the SPEC benchmarks and do a spec2regression somewhere.
def build(target_dir, compile_options, spec_config_name):
    install_dict['compile_options'] = compile_options
    install_dict['spec_config_name'] = spec_config_name
    subprocess.check_call(shlex.split(install_cmd.substitute(install_dict)))

    if target_dir:
        s2r_dict['spec_config_name'] = spec_config_name
        s2r_dict['target_dir'] = target_dir
        subprocess.check_call(shlex.split(s2r_cmd.substitute(s2r_dict)))

# This only installs SPEC, and does not build anything
def install_spec():
    subprocess.check_call([config.spec_install_script, '-j', str(multiprocessing.cpu_count()), '-i', '-d', config.spec_dir])

####################################################################################################
# First diversification form - stackpadding. The benchmarks are compiled using the patched LLVM.
# We create templated commands to install SPEC and get the arguments. Then do the installation
# for the default case and all the stack padding seeds.
####################################################################################################

def main(compile_args=[]):
    # Use the default template linker script to minimize the differences when we started using the shuffled one based on it
    linker.create_linker_script(None)

    # Clean up from possible previous runs
    shutil.rmtree(config.build_dir, True)
    shutil.rmtree(config.extra_build_dir, True)
    os.mkdir(config.extra_build_dir)

    # Install SPEC if necessary
    if not os.path.exists(config.spec_dir):
        install_spec()

    # Some SPEC configuration
    spec_config_name = 'spec2006'

    # Start by compiling for the default binaries
    print('************ Building default binaries... **********')
    compile_options = [config.binary_options, '-mllvm -stackpadding=' + str(config.default_padding)] + compile_args
    extra_options = build_extra(os.path.join(config.extra_build_dir, '0'), compile_options)
    build(support.create_path_for_seeds(config.build_dir), ' '.join(compile_options + extra_options), spec_config_name)
    print('************ Build finished. **********')

    # Then compile for diversfied binaries (stackpadding only)
    for sp_seed, in support.seeds_gen(seed.SPSeed):
        print('************ Building stackpadded binary for seed ' + str(sp_seed) + '... **********')
        # Adapt the arguments so that now we use the real max padding and add random padding
        compile_options = [config.binary_options, '-mllvm -stackpadding=' + str(config.max_padding) + ' -mllvm -padseed=' + str(sp_seed)] + compile_args
        extra_options = build_extra(os.path.join(config.extra_build_dir, str(sp_seed)), compile_options)
        build(support.create_path_for_seeds(config.build_dir, sp_seed), ' '.join(compile_options + extra_options), spec_config_name)
        print('************ Build finished. **********')

if __name__ == '__main__':
    main()
