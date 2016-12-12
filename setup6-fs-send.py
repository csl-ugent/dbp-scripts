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
	#fs_seed = rList[3*j+1]
	pathFrom_8_nofs = '/home/mohit/updated-dBp/build/no-fp/8/fs/' +str(fs_seed)+'/'+ benchmark + '/'
        pathFrom_256_nofs = '/home/mohit/updated-dBp/build/no-fp/256/' + str(sp_seed) + '/fs/'+str(fs_seed)+'/' + benchmark + '/'
	pathTo_8 = '/home/mmishra/binaries/8/' 
	pathTo_256 = '/home/mmishra/binaries/256/'
	name = benchmark.split('.')[1]
        if benchmark == "482.sphinx3":
                name = "sphinx_livepretend"
        if benchmark == "483.xalancbmk":
                name = "Xalan"
	pathFrom_8_nofs = pathFrom_8_nofs + name
	pathFrom_256_nofs = pathFrom_256_nofs + name
	os.system('scp -P 917 ' + pathFrom_8_nofs + ' mmishra@tyr.elis.ugent.be:' + pathTo_8)
	os.system('scp -P 917 ' + pathFrom_256_nofs + ' mmishra@tyr.elis.ugent.be:' + pathTo_256)
	
    

