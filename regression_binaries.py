#!/usr/bin/python3
import itertools
import os
import subprocess

# Import own modules
import config
import support

def regression(build_dir):
    for (benchmark, name) in support.benchmarks_gen():
        print('************ Regression testing ' + build_dir + '/' + benchmark + ' **********')
        result = subprocess.check_output([config.regression_script, '-c', os.path.join(build_dir, 'spec2006_test.conf'), '-t', '-d', config.fake_diablo_dir, '-p', config.fake_diablo_bin, name], stderr=subprocess.DEVNULL, universal_newlines=True).splitlines()[-1]
        print(result)

print('************ Regression testing protected binaries **********')
regression(support.create_path_for_seeds(config.build_dir))
for seed_tuple in support.seeds_gen():
    for subset in support.subsets_gen(seed_tuple, False):
        regression(support.create_path_for_seeds(config.build_dir, *subset))
