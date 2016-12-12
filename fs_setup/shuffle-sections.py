'''
text-sections shuffling
Author: Mohit Mishra
Last Updated: July 13, 2015
'''

import os, random

benchmark_list = ["403.gcc",'400.perlbench','401.bzip2','429.mcf','433.milc','444.namd','445.gobmk','450.soplex','453.povray','456.hmmer','458.sjeng','462.libquantum','464.h264ref','470.lbm','471.omnetpp','473.astar','482.sphinx3','483.xalancbmk','998.specrand']

randomseed = ['3','303','3003']


for stackpad in ['8','256']:
	mkdir_shuffled = "/home/mohit/dBp/function-shuffling/shuffled-"+stackpad+"/"
	#os.system("rm -rf "+mkdir_shuffled)
	#os.system("mkdir -p "+mkdir_shuffled)
	for seed in randomseed:		
		for benchmark in ['401.bzip2']:		    
		    arr_open = open("/home/mohit/dBp/function-shuffling/extract-text-"+stackpad+"/"+benchmark)
		    arr = arr_open.readlines()
		    larray = arr
		    random.seed(seed)
		    random.shuffle(larray)
		    f = open(mkdir_shuffled+benchmark.split('.')[-1]+"-"+seed+".xc","w")
		    ld1_open = open("/home/mohit/dBp/function-shuffling/ld1","r")
		    ld1 = ld1_open.readlines()
		    ld2_open = open("/home/mohit/dBp/function-shuffling/ld2","r")
		    ld2 = ld2_open.readlines()

		    for l1 in ld1:
		        f.write(l1)

		    for i in larray:
		        i = i.strip('\n').strip('\n')
		        f.write("\t"+i+"\n")

		    for l2 in ld2:
		        f.write(l2)

		    ld1_open.close()
		    ld2_open.close()
		    arr_open.close()
		    f.close()


