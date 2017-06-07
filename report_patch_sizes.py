#!/usr/bin/python3
import os
import pyexcel

# Import own modules
import config
import seed
import support

def main():
    # Create the report
    print('************ Creating report on patch sizes **********')
    sheets = {}
    for subset in support.subsets_gen(seed.get_types(), False):
        # Create the sheet for this subset and put it in the dictionary
        name = ','.join([t.__name__ for t in subset]) # Create the sheet name out of the typenames of the seeds in the subset
        sheet = pyexcel.Sheet(name=name)
        sheets[name] = sheet

        # Create the first few columns. The first is for the benchmarks, second is average, and third is max (to be filled in later).
        rownames = [benchmark for benchmark,_ in support.benchmarks_gen()]
        sheet.column += ['Patch sizes'] + rownames
        sheet.column += ['AVG'] * (len(rownames) +1)
        sheet.column += ['MAX'] * (len(rownames) +1)
        for seed_tuple in support.seeds_gen(*subset):
            # Get all the sizes of the patches
            sizes = ['']
            for benchmark, _ in support.benchmarks_gen():
                patch = os.path.join(support.create_path_for_seeds(config.patches_dir, *seed_tuple), benchmark, 'patch')
                if os.path.exists(patch):
                    sizes.append(os.stat(patch).st_size)
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
    report.save_as(os.path.join(config.reports_dir, 'patch_sizes.ods'))

if __name__ == '__main__':
    main()
