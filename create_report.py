#!/usr/bin/python3
import pyexcel
import os

# Import own modules
import config
import seed
import support

# Create the report
print('************ Creating report **********')
sheets = {}
for subset in support.subsets_gen(seed.get_types(), False):
    # Create the sheet for this subset and put it in the dictionary
    name = ','.join([t.__name__ for t in subset]) # Create the sheet name out of the typenames of the seeds in the subset
    sheet = pyexcel.Sheet(name=name)
    sheets[name] = sheet

    # Create the first few columns. The first is for the benchmarks, second is average, and third is max (to be filled in later).
    rownames = [benchmark for benchmark,_ in support.benchmarks_gen()]
    sheet.column += ['Patches uncompressed'] + rownames + ['Patches compressed'] + rownames
    sheet.column += [''] * (len(rownames) +1) + ['AVG'] + [''] * len(rownames)
    sheet.column += [''] * (len(rownames) +1) + ['MAX'] + [''] * len(rownames)
    for seed_tuple in support.seeds_gen(*subset):
        # Empty cell
        sizes = ['']
        
        # Get all the sizes of the patches
        for benchmark, _ in support.benchmarks_gen():
            patch = os.path.join(support.create_path_for_seeds(config.patches_dir, *seed_tuple), benchmark, 'patch')
            sizes.append(os.stat(patch).st_size)

        # Empty cell
        sizes.append('')

        # Get all the sizes of the compressed patches
        for benchmark, _ in support.benchmarks_gen():
            patch = os.path.join(support.create_path_for_seeds(config.patches_dir, *seed_tuple), benchmark, 'patch.bz2')
            sizes.append(os.stat(patch).st_size)

        sheet.column += sizes

    # Calculate in the average and the max
    for row in (row for row in sheet.rows() if not row[0].startswith('Patches')):
        sizes = row[3:]
        row[1] = int(sum(sizes) / len(sizes))
        row[2] = max(sizes)

# Create the report book and write it out
report = pyexcel.Book(sheets=sheets)
report.save_as(os.path.join(config.base_dir, 'report.ods'))
