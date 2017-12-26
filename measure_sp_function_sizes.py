#!/usr/bin/python3
import itertools
import os
import pyexcel

# Import own modules
import build_binaries
import config
import support
from linker import Map

def get_functions(mapfile):
    linkermap = Map(mapfile)
    functions = []
    for section in itertools.chain(linkermap.pre_sections, linkermap.shuffle_sections):
        name = section.name[len('.text.'):]
        functions.append((name, section.size))

    return functions

def main():
    build_dir = os.path.join(config.tmp_dir, 'spec_measurements')
    spec_config_name = 'measuring'

    # Get all the sizes of the default binaries
    sheets = {}
    build_binaries.build_spec(build_dir, ' '.join([config.binary_options]), spec_config_name)
    print('************ Building default binaries... **********')
    for (benchmark, name) in support.benchmarks_gen():
        sheet = pyexcel.Sheet(name=benchmark)
        sheets[benchmark] = sheet
        mapfile = os.path.join(build_dir, benchmark, name + '.map')
        functions = get_functions(mapfile)

        # Add the names and original sizes columns
        names = [''] + [name for (name,_) in functions]
        sheet.column += names
        sizes = ['Original'] + [size for _,size in functions]
        sheet.column += sizes

    # Then compile for diversfied binaries (stackpadding only)
    for max_padding in range(config.default_padding, config.max_padding + 8, 8):
        print('************ Building stackpadded binary with SP ' + str(max_padding) + '... **********')
        # Adapt the arguments so that now we use the real max padding and add random padding
        compile_options = [config.binary_options, '-mllvm -stackpadding=' + str(max_padding)]
        build_binaries.build_spec(build_dir, ' '.join(compile_options), spec_config_name)
        for (benchmark, name) in support.benchmarks_gen():
            sheet = sheets[benchmark]
            mapfile = os.path.join(build_dir, benchmark, name + '.map')
            functions = get_functions(mapfile)

            # Add the sizes and size increases columns
            sizes = ['Pad ' + str(max_padding)] + [size for _,size in functions]
            sheet.column += sizes
            increases = ['Increase ' + str(max_padding)]
            for size1, size2 in list(zip(sheet.column[1], sizes))[1:]:
                increases.append(size2 - size1)
            sheet.column += increases
            increases = ['Increase2base ' + str(max_padding)]
            for size1, size2 in list(zip(sheet.column[2], sizes))[1:]:
                increases.append(size2 - size1)
            sheet.column += increases

    # Create the report book and write it out
    for (benchmark, name) in support.benchmarks_gen():
        report = sheets[benchmark]
        report.save_as(os.path.join(config.reports_dir, benchmark + '_sp.csv'))

if __name__ == '__main__':
    main()
