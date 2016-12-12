import os
import random
import time

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

benchmarkList = ['403.gcc','400.perlbench','401.bzip2','429.mcf','433.milc','444.namd','445.gobmk','450.soplex','453.povray','456.hmmer','458.sjeng','462.libquantum','464.h264ref','470.lbm','471.omnetpp','473.astar','482.sphinx3','483.xalancbmk','998.specrand']

randomseed = []
for j in range(0,30):
    randomseed.append(rList[3*j+1])
tfile = open('/home/mohit/updated-dBp/Patches/fs-time','w')
for rand in randomseed:
    os.system('mkdir -p '+'/home/mohit/updated-dBp/Patches/fs/'+str(rand))
    tfile.write('function-shuffling seed = ' + str(rand) + '\n')
    for benchmark in benchmarkList:
    		name = benchmark.split('.')[1]
    		if benchmark == "482.sphinx3":
    			name = "sphinx_livepretend"
		if benchmark == "483.xalancbmk":
    			name = "Xalan"
		pfile = open("/home/mohit/updated-dBp/Patches/fs/"+str(rand)+"/"+name+".patch","w")
		symfile = "/home/mohit/updated-dBp/symfiles/no-fp/8/fs/"+str(rand)+"/"+name+".symfile"
		path = "/home/mohit/updated-dBp/tmp/fs-patching/"
		start_time = time.time()
		os.system("less "+symfile+" | grep \"FUNC\" | cut -d \' \' -f 2,3 > "+path+str(rand)+"-func-addr-size")
		fas = open(path+str(rand)+"-func-addr-size")
		read_func = fas.readlines()
		l = len(read_func)
        	pair = filter(None,read_func[0].strip('\n').split(' '))
        	pfile.write(pair[0]+"\n")
		prev_addr = pair[0]
		prev_size = pair[1]
		k = 0
		for i in range(1, l):
			pair = filter(None,read_func[i].strip('\n').split(' '))
			addr = pair[0]
			size = pair[1]
			offset = int(addr,16)-int(prev_addr,16)
			if not offset == int(prev_size, 16):
				pfile.write(str(i-k) + ":" +hex(int(offset)).split('x')[-1]+"\n")
				k = i
			prev_addr = addr
			prev_size = size
		end_time = time.time()
		tfile.write('\t' + benchmark + ' ' + str(end_time-start_time)+'\n')
		pfile.close()
		fas.close()
		os.system("rm -f " + path + str(rand) + "-func-addr-size") 
tfile.close()
