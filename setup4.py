'''
text-sections shuffling
Author: Mohit Mishra
Last Updated on : April 29, 2016
'''

import os, random

# Get the random seeds from randopm seeds log file
rLogPath = '/home/mohit/updated-dBp/log/random.txt'
rLog = open(rLogPath,'r')
lines = rLog.readlines()
rList = []
k = 1
for line in lines:
   value = int(line.strip('\n'))
   rList.append(value)
   print(str(k) + " - " +(str(value)))
   k = k + 1
rLog.close()

benchmarkList = ["403.gcc",'400.perlbench','401.bzip2','429.mcf','433.milc','444.namd','445.gobmk','450.soplex','453.povray','456.hmmer','458.sjeng','462.libquantum','464.h264ref','470.lbm','471.omnetpp','473.astar','482.sphinx3','483.xalancbmk','998.specrand']

randomseed = []
for j in range(0,30):
    randomseed.append(rList[3*j+1])

root = '/home/mohit/updated-dBp/tmp/func-shuffling/shuffled-sections/'
textSections = '/home/mohit/updated-dBp/tmp/func-shuffling/text-sections/'

if os.path.exists(root):
    os.system('rm -rf ' + root)
os.system('mkdir -p ' + root)
for fs_seed in randomseed:
    os.system('mkdir -p ' + root + '/' + str(fs_seed))
    for benchmark in benchmarkList:
	textSectionsFile = open(textSections + benchmark)
	readSections = textSectionsFile.readlines()
	textSectionsFile.close()
	sectionsArray = readSections
	random.seed(fs_seed)
	random.shuffle(sectionsArray)
	
	f = open(root + str(fs_seed) + '/' + benchmark +'.xc', 'w')
	ld1_open = open("/home/mohit/updated-dBp/scripts/fs_setup/ld1","r")
        ld1 = ld1_open.readlines()
        ld2_open = open("/home/mohit/updated-dBp/scripts/fs_setup/ld2","r")
        ld2 = ld2_open.readlines()

        for l1 in ld1:
                        f.write(l1)

        for i in sectionsArray:
                        i = i.strip('\n').strip('\n')
                        f.write("\t"+i+"\n")

        for l2 in ld2:
                        f.write(l2)

        ld1_open.close()
        ld2_open.close()
        f.close() 

