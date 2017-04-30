#!/usr/bin/python3
import os
import pyexcel
import subprocess

# Import own modules
import config
import support

def get_opportunity_log_size(data_dir):
    # Get the files that are to be put into the opportunity log
    files = os.listdir(data_dir)
    files.remove('build')
    files.remove('symfile')

    # Tar them together
    log = os.path.join(config.tmp_dir, 'opportunity_log')
    subprocess.check_call(['tar', '--create', '--file', log] + files, cwd=data_dir)

    # Compress log
    subprocess.check_call(['bzip2', '--force', log])
    output = os.path.join(config.tmp_dir, 'opportunity_log.bz2')

    return os.stat(output).st_size

# Create the sheet
print('************ Creating report on opportunity log sizes **********')
sheet = pyexcel.Sheet()
rownames = [benchmark for benchmark,_ in support.benchmarks_gen()]
sheet.column += ['Opportunity log'] + rownames

# Get all the sizes of the opportunity logs
sizes = ['']
for (benchmark, name) in support.benchmarks_gen():
    data_dir = os.path.join(support.create_path_for_seeds(config.data_dir), benchmark)
    sizes.append(get_opportunity_log_size(data_dir))

sheet.column += sizes

# Create the report book and write it out
report = pyexcel.Book(sheets={'Sizes' : sheet})
report.save_as(os.path.join(config.reports_dir, 'opportunity_log_sizes.ods'))
