import os
import time

stackpad = ['8','256']
benchmarkList = ["403.gcc",'400.perlbench','401.bzip2','429.mcf','433.milc','444.namd','445.gobmk','450.soplex','453.povray','456.hmmer','458.sjeng','462.libquantum','464.h264ref','470.lbm','471.omnetpp','473.astar','482.sphinx3','483.xalancbmk','998.specrand']
nop_chance = ['10','20','50']

# Get the random seeds from randopm seeds log file
rLogPath = '/home/mohit/updated-dBp/log/random.txt'
rLog = open(rLogPath,'r')
lines = rLog.readlines()
rList = []
k = 1
for line in lines:
   value = int(line.strip('\n'))
   rList.append(value)
   k = k + 1
rLog.close()

os.system('mkdir /home/mohit/updated-dBp/NOPReplayOutput/')
PATH = '/home/mohit/updated-dBp/NOPInsertionLists/no-fp/'
REPLAY = '/home/mohit/updated-dBp/NOPReplayOutput/no-fp/'
tfile = open('/home/mohit/updated-dBp/NOPReplayOutput/nopreplaytiming.txt','w')
for j in range(0, 30):
    sp_seed = rList[3*j]
    fs_seed = rList[3*j+1]
    nop_seed = rList[3*j+2]

    for benchmark in benchmarkList:
        name = benchmark.split('.')[1]
        if benchmark == "482.sphinx3":
            name = "sphinx_livepretend"
        if benchmark == "483.xalancbmk":
                name = "Xalan"
		continue
	if benchmark == '998.specrand':
		continue
        for pad in stackpad:
            for chance in nop_chance:
	        replay_path = ''
	        nopsinsertionlist = ''
	        if pad == '8':
			replay_path = REPLAY + '8/fs/' +str(fs_seed) + '/' + str(nop_seed) + '/' + str(chance) + '/' + name
	    		nopsinsertionlist = PATH + '8/fs/' + str(fs_seed) + '/' + str(nop_seed) + '/' + name + '/' + str(chance) + '/nopsinsertion.list'
	        else:
			replay_path = REPLAY + '256/' + str(sp_seed) + '/fs/' +str(fs_seed) + '/' + str(nop_seed) + '/' + str(chance) + '/' + name
			nopsinsertionlist = PATH + '256/' + str(sp_seed) + '/fs/' + str(fs_seed) + '/' + str(nop_seed) + '/' + name + '/' + str(chance) + '/nopsinsertion.list'
                os.system('mkdir -p ' + replay_path)
	         
	        print nopsinsertionlist
		start_time = time.time()
                os.system("./replay "+str(nop_seed)+" "+str(chance)+" "+nopsinsertionlist+" > " + replay_path + "/nopsinsertion.list")
   	        end_time = time.time()
	        tfile.write(benchmark + 'pad=' + str(pad) + ' j=' + str(j) +' nop_chance=' + str(chance) + ' ' + 'time=' + str(end_time-start_time) + '\n')
tfile.close()
