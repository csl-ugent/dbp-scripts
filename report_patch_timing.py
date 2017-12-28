#!/usr/bin/python3
import os
import pyexcel
import shutil
import timeit

# Import own modules
import config
import patch
import support

def main():
    # Create the sheet
    print('************ Creating report on patch timing **********')
    sheet = pyexcel.Sheet()
    rownames = [benchmark for benchmark,_ in support.benchmarks_gen()]
    sheet.column += ['Patch creation'] + rownames + ['Patch application'] + rownames
    sheet.column += [''] * (len(rownames) +1) + ['AVG'] + [''] * len(rownames)
    sheet.column += [''] * (len(rownames) +1) + ['MAX'] + [''] * len(rownames)

    for seeds in support.all_seeds_gen():
        # Empty cell
        times = ['']

        for (benchmark, name) in support.benchmarks_gen():
            # Determine all paths
            base_data = os.path.join(support.create_path_for_seeds(config.data_dir), benchmark)
            div_symfile_path = os.path.join(support.create_path_for_seeds(config.data_dir, *seeds), benchmark, 'symfile')

            # Time patch creation
            def time_function1():
                patch.patch(base_data, seeds, div_symfile_path=div_symfile_path, output_dir=config.tmp_dir)
            times.append(timeit.timeit(time_function1, number=1))
            shutil.copyfile(os.path.join(config.tmp_dir, 'patch'), os.path.join(config.tmp_dir, 'patch.' + name))

        # Empty cell
        times.append('')

        for (benchmark, name) in support.benchmarks_gen():
            base_data = os.path.join(support.create_path_for_seeds(config.data_dir), benchmark)
            # Time patch application
            def time_function2():
                patch.patch(base_data, seeds, patch_path=os.path.join(config.tmp_dir, 'patch.' + name), output_dir=config.tmp_dir)
            times.append(timeit.timeit(time_function2, number=1))

        sheet.column += times

    # Calculate in the average and the max
    for row in (row for row in sheet.rows() if not row[0].startswith('Patch')):
        times = [elem for elem in row[3:] if isinstance(elem, float)]
        if times:
            row[1] = float(sum(times) / len(times))
            row[2] = max(times)

    # Create the report book and write it out
    report = pyexcel.Book(sheets={'Timing' : sheet})
    report.save_as(os.path.join(config.reports_dir, 'patch_timing.ods'))

if __name__ == '__main__':
    main()
