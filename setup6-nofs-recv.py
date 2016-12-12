import os, sys

input_ri = int(sys.argv[1]) # compilation number

benchmarkList =["403.gcc",'400.perlbench','401.bzip2','429.mcf','433.milc','444.namd','445.gobmk','450.soplex','453.povray','456.hmmer','458.sjeng','462.libquantum','464.h264ref','470.lbm','471.omnetpp','473.astar','482.sphinx3','483.xalancbmk','998.specrand']
# first fetch the seeds from random.log
rLogPath = '/home/mohit/updated-dBp/log/random.txt'
rLog = open(rLogPath,'r')
lines = rLog.readlines()
rList = []

sp_seed = int(lines[3*input_ri].strip('\n'))
fs_seed = int(lines[3*input_ri + 1].strip('\n'))
'''
k = 1
for line in lines:
   value = int(line.strip('\n'))
   rList.append(value)
   print(str(k) + " - " +(str(value)))
   k = k + 1

rLog.close()
'''

print(' Sending binaries to the ARM Boards ....... ')


for i in range(0,1):
    j = input_ri
    print('************* Compilation #' + str(j)+'******************')
    for benchmark in benchmarkList:
	print('\t'+benchmark)
        #sp_seed = rList[3*j]
	#fs_seed = rList[3*j+1]i
	print(sp_seed)
	pathTo_8_nofs = '/home/mohit/updated-dBp/symfiles/no-fp/8/no-fs/'
        pathTo_256_nofs = '/home/mohit/updated-dBp/symfiles/no-fp/256/' + str(sp_seed) + '/no-fs/'
	pathFrom_8 = '/home/mmishra/symfiles/8/' 
	pathFrom_256 = '/home/mmishra/symfiles/256/'
	name = benchmark.split('.')[1]
        if benchmark == "482.sphinx3":
                name = "sphinx_livepretend"
        if benchmark == "483.xalancbmk":
                name = "Xalan"
	name = name +'.symfile'
	os.system('scp -P 917  mmishra@tyr.elis.ugent.be:' + pathFrom_8 + name + ' ' +pathTo_8_nofs)
	os.system('scp -P 917  mmishra@tyr.elis.ugent.be:' + pathFrom_256 + name + ' ' + pathTo_256_nofs)
	
    

