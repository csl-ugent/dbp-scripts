import os
import sys

benchmarkList =["403.gcc",'400.perlbench','401.bzip2','429.mcf','433.milc','444.namd','445.gobmk','450.soplex','453.povray','456.hmmer','458.sjeng','462.libquantum','464.h264ref','470.lbm','471.omnetpp','473.astar','482.sphinx3','483.xalancbmk','998.specrand']
nopChance = ['10','20','50']
stackpad = ['8','256']
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

p1 = "/home/mohit/diablo-source/mishra/build/diablo-arm-nop -Z -kco -exidx --no-merge-exidx --nopinsertionchance "
p2 = " --nopinsertionseed "

for j in range(0, 30):
    sp_seed = str(rList[3*j])
    fs_seed = str(rList[3*j+1])
    nop_seed = str(rList[3*j+2])
    for benchmark in benchmarkList:
	name = benchmark.split('.')[1]
        if benchmark == "482.sphinx3":
            name = "sphinx_livepretend"
        if benchmark == "483.xalancbmk":
                name = "Xalan"
	for pad in stackpad:
            # benchmark's path
            b = "/home/mohit/updated-dBp/build/no-fp/"
            # nop lists path
            nopListsPath = "/home/mohit/updated-dBp/NOPInsertionLists/no-fp/"

            if pad == '256':
                b = b + sp_seed + "/fs/"+fs_seed+"/"+benchmark
                nopListsPath = nopListsPath + sp_seed + "/fs/"+fs_seed+"/"+name
            else:
                b = b + "/fs/"+fs_seed+"/"+benchmark
                nopListsPath = nopListsPath + "/fs/"+fs_seed+"/"+name
    	    for chance in nopChance:
	        os.system('cp ' + b + '/' + name +' ' + b + '/' + name + '-' + nop_seed + '-' + chance)
		os.system('egrep -v \'mohit.bjorn\' ' + b + '/' + name + '.map > ' + b + '/' + name + '-' + nop_seed + '-' + chance + '.map') 
		nopChancePath = nopListsPath + "/"+chance
                goto = "cd "+ b
                s1 = "cp "+b+"/nopsinsertion.list " + nopChancePath + "/"             
                boutlist = "cp " + b + "/b.out.list " + nopChancePath + "/"
                bout = "cp "+b+"/b.out "+nopChancePath+"/"
                # binary's path
                p2b = b+"/"+benchmark+"/"+name+"-"+nop_seed+"-"+chance
                cmd = "cd "+ b +";"+p1+str(chance)+p2+str(nop_seed)+" "+p2b+";"+s1+";"+boutlist+";"+bout
                print cmd1
                start_time = time.time()
                os.system(cmd)
                end_time = time.time()
                t.file(benchmark + ' ' + stackpad + ' ' + sp_seed + ' ' + fs_seed + ' ' + nop_seed + ' ' + ' ' + chance + ' ' + str(end_time-start_time)+'\n')
