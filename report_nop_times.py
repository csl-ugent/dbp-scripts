#!/usr/bin/python3
import logging
import os
import pyexcel
import shlex
import subprocess
import timeit

# Import own modules
import config
import seed
import support

def time_diablo(name, nop_seed, input_dir, output_dir):
    try:
        print('************ Inserting NOPs for ' + input_dir + ' with nop_seed ' + str(nop_seed) + ' **********')

        print(subprocess.list2cmdline([config.diablo_bin, '-O', input_dir, '-o', name] + shlex.split(config.diablo_options) + ['--nopinsertionchance', str(config.nop_chance),
            '--nopinsertionseed', str(nop_seed), os.path.join(input_dir, name)]))

        return timeit.timeit(time_function1, number=1)
    except Exception:
        logging.getLogger().exception('NOP insertion failed for ' + input_dir + '/' + str(nop_seed))

def main():
    # Create the sheet
    print('************ Timing NOP insertion using Diablo **********')
    sheet = pyexcel.Sheet()
    rownames = [benchmark for benchmark,_ in support.benchmarks_gen()]
    sheet.column += ['NOP insertion times'] + rownames
    sheet.column += ['AVG'] + [''] * len(rownames)
    sheet.column += ['MAX'] + [''] * len(rownames)

    for (sp_seed, fs_seed, nop_seed) in support.seeds_gen(seed.SPSeed, seed.FSSeed, seed.NOPSeed):
        # Empty cell
        times = ['']
        for (benchmark, name) in support.benchmarks_gen():
            input_dir = os.path.join(support.create_path_for_seeds(config.build_dir, sp_seed, fs_seed), benchmark)
            output_dir = os.path.join(support.create_path_for_seeds(config.build_dir, sp_seed, fs_seed, nop_seed), benchmark)
            times.append(time_diablo(name, nop_seed, input_dir, output_dir))

        sheet.column += times

    # Calculate in the average and the max
    for row in list(sheet.rows())[1:]:
        times = [elem for elem in row[3:] if isinstance(elem, float)]
        if times:
            row[1] = float(sum(times) / len(times))
            row[2] = max(times)

    # Create the report book and write it out
    report = pyexcel.Book(sheets={'NOP insertion times' : sheet})
    report.save_as(os.path.join(config.reports_dir, 'nop_insertion_times.ods'))

if __name__ == '__main__':
    main()
