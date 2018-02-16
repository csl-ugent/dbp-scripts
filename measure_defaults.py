#!/usr/bin/python3
import argparse
import os
import pyexcel
import shlex
import shutil
import subprocess
import timeit

# Import own modules
import build_binaries
import config
import stacktrace
import support
from support import hex_int

def replace_main_with_bkpt(binary):
    # Get the VMA and offset of the .text section
    for line in subprocess.check_output(['objdump', '-h', binary], universal_newlines=True).splitlines():
        tokens = line.split()
        if len(tokens) == 7 and tokens[1] == '.text':
            text_vma = hex_int(tokens[3])
            text_offset = hex_int(tokens[5])
            break

    # Get the VMA of the 'main' symbol
    for line in subprocess.check_output(['objdump', '-t', binary], universal_newlines=True).splitlines():
        tokens = line.split()
        if tokens and tokens[-1] == 'main':
            main_vma = hex_int(tokens[0])
            break

    # Calculate the offset of the main symbol within the binary
    main_offset = text_offset + (main_vma - text_vma)

    # Write a bkpt on this offset
    with open(binary, 'r+b') as f_bin:
        f_bin.seek(main_offset)
        f_bin.write(bytes.fromhex('700020e1'))

def time_report_creation(benchmark, name, build_dir, run_dir):
    binary = os.path.join(build_dir, benchmark, name)

    # Adapt the binary to put a BKPT on its main
    replace_main_with_bkpt(binary)

    # Run the regression script for the binary and get its stdout
    output = subprocess.check_output([config.regression_script, '-c', os.path.join(build_dir, 'spec2006_test.conf'), '-T', run_dir,
        '-d', config.fake_diablo_dir, '-p', config.fake_diablo_bin, name], stderr=subprocess.DEVNULL, universal_newlines=True)

    # Get the first dump
    dump = stacktrace.get_dumps_for_output(output, benchmark, run_dir)[0]

    # Create the symfile
    symfile = os.path.join(run_dir, 'symfile')
    with open(symfile, 'w') as f_sym:
        subprocess.check_call([config.dump_syms, binary], stdout=f_sym, stderr=subprocess.DEVNULL)

    # Set up the symbols directory for stackwalk
    symbols_dir = stacktrace.setup_symbols_dir_for_dump(dump, symfile, name, run_dir)

    # Create the stacktrace and time how long it takes
    def time_function1():
        subprocess.check_output([config.minidump_stackwalk, dump, symbols_dir], stderr=subprocess.DEVNULL, universal_newlines=True)
    return (timeit.timeit(time_function1, number=30) / 30)

def measure_crash_report_time(build_dir):
    # Create the sheet
    print('************ Measuring the time it takes to create stack traces from a minidump **********')
    sheet = pyexcel.Sheet()
    rownames = [benchmark for benchmark,_ in support.benchmarks_gen()]
    sheet.column += rownames

    # Generate the times and fill in the sheet
    run_dir = os.path.join(config.tmp_dir, 'measurements')
    shutil.rmtree(run_dir, True)
    os.mkdir(run_dir)
    times = []
    for (benchmark, name) in support.benchmarks_gen():
        print('************ ' + benchmark + ' **********')
        times.append(time_report_creation(benchmark, name, build_dir, run_dir))
    sheet.column += times

    # Create the report book and write it out
    report = pyexcel.Book(sheets={'Crash report creation times' : sheet})
    report.save_as(os.path.join(config.reports_dir, 'crash_report_creation_times.ods'))

def measure_compilation_time(build_dir):
    # Create the sheet
    print('************ Measuring the compilation times **********')
    sheet = pyexcel.Sheet()
    rownames = [benchmark for benchmark,_ in support.benchmarks_gen()]
    sheet.column += rownames

    # Time how long it takes to build the benchmark using the timeit module, and the commands in the make.out
    # file present in the build directory.
    def build_time(benchmark_dir):
        os.chdir(benchmark_dir)
        return (timeit.timeit('subprocess.check_call(["bash", "make.out"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)', number=30, setup='import subprocess') / 30)

    # Fill in the sheet
    times = []
    for benchmark, _ in support.benchmarks_gen():
        print('************ ' + benchmark + ' **********')
        benchmark_dir = os.path.join(build_dir, benchmark)
        times.append(build_time(benchmark_dir))
    sheet.column += times

    # Create the report book and write it out
    report = pyexcel.Book(sheets={'Compilation times' : sheet})
    report.save_as(os.path.join(config.reports_dir, 'compilation_times.ods'))

def time_benchmark(build_dir, name):
    result = subprocess.check_output([config.regression_script, '-c', os.path.join(build_dir, 'spec2006_train.conf'), '-i', '-t', '-d', config.fake_diablo_dir, '-p', config.fake_diablo_bin, name], stderr=subprocess.DEVNULL, universal_newlines=True).splitlines()[-1]
    return float(result.split()[-1])

def measure_benchmark_time(build_dir, build_dir_opt):
    # Create the sheet
    print('************ Measuring the benchmark timing **********')
    sheet = pyexcel.Sheet()
    rownames = [benchmark for benchmark,_ in support.benchmarks_gen()]
    sheet.column += ['Without Clang OPT'] + rownames + ['With Clang OPT'] + rownames
    sheet.column += ['AVG'] + [''] * len(rownames) + ['AVG'] + [''] * len(rownames)
    sheet.column += ['MAX'] + [''] * len(rownames) + ['MAX'] + [''] * len(rownames)
    nr_of_measurements = 10
    for _ in range(nr_of_measurements):
        sheet.column += [''] * (2 + 2 * len(rownames))

    for bi, (_, name) in enumerate(support.benchmarks_gen()):
        print('************ Benchmark ' + name + ' **********')

        # Burn some benchmarks to prepare cache/environment
        time_benchmark(build_dir, name)
        time_benchmark(build_dir_opt, name)

        # Do the actual measurements, alternating between the version with and without optimization
        for iii in range(nr_of_measurements):
            col = iii +3
            sheet[1 + bi, col] = time_benchmark(build_dir, name)
            sheet[2 + len(rownames) + bi, col] = time_benchmark(build_dir_opt, name)

    # Calculate in the average and the max
    for row in (row for row in sheet.rows() if not row[0].startswith('With')):
        times = [elem for elem in row[3:] if isinstance(elem, float)]
        if times:
            row[1] = float(sum(times) / len(times))
            row[2] = max(times)

    # Create the report book and write it out
    report = pyexcel.Book(sheets={'Execution time' : sheet})
    report.save_as(os.path.join(config.reports_dir, 'benchmark_times.ods'))

def main():
    # Parsing the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--arguments', type=str, default='', help='Extra compiler arguments to be used.')
    parser.add_argument('-k', '--keep_build', action='store_true', help='Keep the build directory, do not rebuild.')
    parser.add_argument('-c', '--compilation_time', action='store_true', help='Measure the compilation time.')
    parser.add_argument('-r', '--crash_report_time', action='store_true', help='Measure the crash report time.')
    parser.add_argument('-b', '--benchmark_time', action='store_true', help='Measure the benchmark time.')
    args = parser.parse_args()

    # If no measurement was specified, do all
    if not args.compilation_time and not args.crash_report_time and not args.benchmark_time:
        args.compilation_time = True
        args.crash_report_time = True

    # Default compilation options
    compile_options = build_binaries.get_default_compile_options() + [args.arguments]
    extra_build_dir = os.path.join(config.tmp_dir, 'spec_measurements_extra')

    # As we want to compare two SPEC builds we expect this one to be built with differing options (or a compiler
    # with differing behavior as in our case).
    if args.benchmark_time:
        assert args.keep_build, 'Keep previous build was not specified. A SPEC build must already be provided!'
        build_dir_opt = os.path.join(config.tmp_dir, 'spec_measurements_opt')
        extra_options = build_binaries.build_extra(extra_build_dir, compile_options)
        build_binaries.build_spec(build_dir_opt, ' '.join(compile_options + extra_options), 'measurements')

    # Build the benchmarks. No protections at all (not even default stack padding), but with added breakpad.
    build_dir = os.path.join(config.tmp_dir, 'spec_measurements')
    if not args.keep_build:
        extra_options = build_binaries.build_extra(extra_build_dir, compile_options)
        build_binaries.build_spec(build_dir, ' '.join(compile_options + extra_options), 'measurements')

    # Do the measurements (crash reporting last as it changes the binary)
    if args.compilation_time:
        measure_compilation_time(build_dir)
    if args.benchmark_time:
        measure_benchmark_time(build_dir, build_dir_opt)
    if args.crash_report_time:
        measure_crash_report_time(build_dir)

if __name__ == '__main__':
    main()
