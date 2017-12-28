#!/usr/bin/python3
import os
import pyexcel

# Import own modules
import config
import support

def main():
    # Create the sheet
    print('************ Creating report on symfile sizes **********')
    sheet = pyexcel.Sheet()
    rownames = [benchmark for benchmark,_ in support.benchmarks_gen()]
    sheet.column += ['Symfile default'] + rownames + ['Symfile diversified'] + rownames

    # Get all the sizes of the default symfiles
    sizes = ['']
    for (benchmark, name) in support.benchmarks_gen():
        symfile = os.path.join(support.create_path_for_seeds(config.data_dir), benchmark, 'symfile')
        if os.path.exists(symfile):
            sizes.append(os.stat(symfile).st_size)
        else:
            sizes.append('FAIL')

    # Create the AVG and MAX columns
    sheet.column += sizes + ['AVG'] + [''] * len(rownames)
    sheet.column += sizes + ['MAX'] + [''] * len(rownames)

    for seeds in support.all_seeds_gen():
        # Get all the sizes of the diversified symfiles
        sizes = [''] * (len(rownames) +2)
        for (benchmark, name) in support.benchmarks_gen():
            symfile = os.path.join(support.create_path_for_seeds(config.data_dir, *seeds), benchmark, 'symfile')
            if os.path.exists(symfile):
                sizes.append(os.stat(symfile).st_size)
            else:
                sizes.append('FAIL')

        sheet.column += sizes

    # Calculate in the average and the max
    for row in (row for row in sheet.rows() if not row[0].startswith('Symfile')):
        sizes = [elem for elem in row[3:] if isinstance(elem, int)]
        if sizes:
            row[1] = sum(sizes) // len(sizes)
            row[2] = max(sizes)

    # Create the report book and write it out
    report = pyexcel.Book(sheets={'Sizes' : sheet})
    report.save_as(os.path.join(config.reports_dir, 'symfile_sizes.ods'))

if __name__ == '__main__':
    main()
