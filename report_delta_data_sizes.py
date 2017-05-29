#!/usr/bin/python3
import os
import pyexcel

# Import own modules
import config
import seed
import support

def main():
    # Create the report
    print('************ Creating report on delta data sizes **********')
    sheets = {}
    for subset in support.subsets_gen(seed.get_types(), False):
        # Create the sheet for this subset and put it in the dictionary
        name = ','.join([t.__name__ for t in subset]) # Create the sheet name out of the typenames of the seeds in the subset
        sheet = pyexcel.Sheet(name=name)
        sheets[name] = sheet

        # Create the first few columns. The first is for the benchmarks, second is average, and third is max (to be filled in later).
        rownames = [benchmark for benchmark,_ in support.benchmarks_gen()]
        sheet.column += ['Delta data'] + rownames
        sheet.column += ['AVG'] + [''] * len(rownames)
        sheet.column += ['MAX'] + [''] * len(rownames)
        for seed_tuple in support.seeds_gen(*subset):
            # Empty cell
            sizes = ['']

            # Get all the sizes of the patches
            for benchmark, _ in support.benchmarks_gen():
                dd = os.path.join(support.create_path_for_seeds(config.patches_dir, *seed_tuple), benchmark, 'delta_data')
                if os.path.exists(dd):
                    sizes.append(os.stat(dd).st_size)
                else:
                    sizes.append('FAIL')

            sheet.column += sizes

        # Calculate in the average and the max
        for row in list(sheet.rows())[1:]:
            sizes = [elem for elem in row[3:] if isinstance(elem, int)]
            if sizes:
                row[1] = sum(sizes) // len(sizes)
                row[2] = max(sizes)

    # Create the report book and write it out
    report = pyexcel.Book(sheets=sheets)
    report.save_as(os.path.join(config.reports_dir, 'delta_data_sizes.ods'))

if __name__ == '__main__':
    main()
