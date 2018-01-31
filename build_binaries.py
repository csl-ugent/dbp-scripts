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

# Builds all extra source code (such as the breakpad client archive) with the requested options. Returns the extra
# compile options that are required to link with the resulting objects/archives.
def build_extra(build_dir, compile_options):
    # Create the build directory (after cleaning up possible previous run)
    shutil.rmtree(build_dir, True)
    os.makedirs(build_dir)
    ret_options = [config.breakpad_options]

    print('************ Building dump object **********')
    dump_build_dir = os.path.join(build_dir, 'dump')
    shutil.copytree(config.dump_dir, dump_build_dir)
    subprocess.check_call(['make', 'CXX=' + config.clang_bin, 'CPPFLAGS=' + ' '.join(compile_options) + ' -I' + os.path.join(config.breakpad_dir, 'src')], cwd=dump_build_dir, stdout=subprocess.DEVNULL)
    ret_options.append('-Wl,--library-path=' + dump_build_dir)
    ret_options.append('-Wl,--library=:dump.o')
    os.symlink(dump_build_dir, os.path.join(dump_build_dir, 'build')) # Build prefix

    # Build the breakpad archive
    print('************ Building breakpad archive **********')
    breakpad_build_dir = os.path.join(build_dir, 'breakpad')
    os.makedirs(breakpad_build_dir)
    subprocess.check_call([os.path.join(config.breakpad_dir, 'configure'), '--host=' + config.target_triple, '--disable-tools', '--disable-processor',
        'CC=' + config.clang_bin, 'CXX=' + config.clang_bin, 'CFLAGS=' + ' '.join(compile_options), 'CXXFLAGS=' + ' '.join(compile_options)], cwd=breakpad_build_dir, stdout=subprocess.DEVNULL)
    subprocess.check_call(['make'], cwd=breakpad_build_dir, stdout=subprocess.DEVNULL)
    ret_options.append('-Wl,--library-path=' + breakpad_build_dir)
    ret_options.append('-Wl,--library=:' + config.breakpad_archive)
    os.symlink(os.path.join(breakpad_build_dir, config.breakpad_archive), os.path.join(breakpad_build_dir, 'build')) # Build prefix

    return ret_options

# Build the SPEC benchmarks and do a spec2regression somewhere.
def build_spec(target_dir, compile_options, spec_config_name='spec2006'):
    install_dict = {
        'binary' : config.spec_install_script,
        'clang_dir': config.clang_dir,
        'compile_options': compile_options,
        'concurrency': multiprocessing.cpu_count() -1,
        'cross_toolchain_dir': config.cross_toolchain_dir,
        'target_triple': config.target_triple,
        'link_script': config.link_script,
        'spec_config_name': spec_config_name,
        'spec_dir': config.spec_dir
    }

    install_cmd = Template('$binary -r -j $concurrency -D -d $spec_dir -c $spec_config_name -t $cross_toolchain_dir -p $target_triple -C $clang_dir '
            '-O "${compile_options} -Wl,--no-demangle -Wl,--hash-style=sysv -Wl,--no-merge-exidx-entries -Wl,--allow-shlib-undefined -Wl,-T $link_script"')
    subprocess.check_call(shlex.split(install_cmd.substitute(install_dict)))

    if target_dir:
        s2r_dict = {
            'binary' : config.spec2regression_script,
            'spec_dir': config.spec_dir,
            'spec_config_name': spec_config_name,
            'ssh_params': config.ssh_params,
            'target_dir': target_dir
        }

        s2r_cmd = Template('$binary -s "${ssh_params}" -p $spec_dir -b build_base_${spec_config_name}-nn.0000 -t 5000 -d $target_dir')
        subprocess.check_call(shlex.split(s2r_cmd.substitute(s2r_dict)))

def main(compile_args=[]):
    # Use the default template linker script to minimize the differences when we start protecting at link time
    linker.create_linker_script(None)

    # Clean up from possible previous runs
    shutil.rmtree(config.build_dir, True)
    shutil.rmtree(config.extra_build_dir, True)
    os.mkdir(config.extra_build_dir)

    # Start by compiling for the default binaries. Build up the compile options, starting from the binary options, adding the default
    # compile options for the diferent protections, then the compile arguments passed on the command line.
    print('************ Building default binaries... **********')
    default_compile_options = [config.binary_options]
    for protection in seed.get_types():
        default_compile_options += protection.default_compile_options
    compile_options = default_compile_options + compile_args

    # We start building the extra binaries, and add their extra compile options to the ones we use to build SPEC.
    compile_options += build_extra(support.create_path_for_seeds(config.extra_build_dir), compile_options)
    build_spec(support.create_path_for_seeds(config.build_dir), ' '.join(compile_options))
    print('************ Build finished. **********')

    # Next we compile the protected binaries. We build up the compile options, starting from the binary options, adding the
    # compile options for the different protections (based on the associated seed), then the compile arguments passed on the
    # command line.
    for protections in support.build_subsets_gen(seed.get_types(), False):
        for seeds in support.seeds_gen(*protections):
            print('************ Building protected binary for ' + ' '.join([repr(s) for s in seeds]) + ' ... **********')
            compile_options = list(default_compile_options)
            for s in seeds:
                compile_options += s.diversify_build()
            compile_options += compile_args

            # We start building the extra binaries, and add their extra compile options to the ones we use to build SPEC.
            compile_options += build_extra(support.create_path_for_seeds(config.extra_build_dir, *seeds), compile_options)
            build_spec(support.create_path_for_seeds(config.build_dir, *seeds), ' '.join(compile_options))
            print('************ Build finished. **********')

if __name__ == '__main__':
    main()
