import os
import sys
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

nop_chance = ['10','20','50']
stackpad = ['8', '256']

benchmarkList = ["403.gcc",'400.perlbench','401.bzip2','429.mcf','433.milc','444.namd','445.gobmk','450.soplex','453.povray','456.hmmer','458.sjeng','462.libquantum','464.h264ref','470.lbm','471.omnetpp','473.astar','482.sphinx3','483.xalancbmk','998.specrand']
nop_chance = ['10','20','50']
stackpad = ['8','256']

p1 = "/home/mohit/diablo-source/mishra/build/diablo-arm-nop -Z -kco -exidx --no-merge-exidx --nopinsertionchance "
p2 = " --nopinsertionseed "

tfile = open('/home/mohit/updated-dBp/Patches/noplists_creation.txt','w')
for j in range(0, 1):
    sp_seed = str(rList[3*j])
    fs_seed = str(rList[3*j+1])
    nop_seed = str(rList[3*j+2])
    for benchmark in ['403.gcc']:
	print benchmark
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
                b = b + "/256/" + sp_seed + "/fs/"+fs_seed+"/"+benchmark
                nopListsPath = nopListsPath + "/256/" + sp_seed + "/fs/"+fs_seed+"/"+name
            else:
                b = b + "/8/fs/"+fs_seed+"/"+benchmark
                nopListsPath = nopListsPath + "/8/fs/"+fs_seed+"/"+name

            for nop in nop_chance:
                nopChancePath = nopListsPath + "/"+nop
		os.system('mkdir -p ' + nopChancePath)
                goto = "cd "+ b
                s1 = "cp "+b+"/nopsinsertion.list "+nopChancePath+"/"             
                boutlist = "cp "+b+"/b.out.list "+nopChancePath+"/"
                bout = "cp "+b+"/b.out "+nopChancePath+"/"
		# cd into the benchmark
                cmd1 = "cd "+ b+";"
		# insert nop using diablo 
		cmd2 = p1+str(nop)+p2+str(nop_seed)+" "+name+";"
		# copy b.out.list and nopsinsertion.list to nopChancePath
		cmd3 = s1+";"+boutlist+";"+bout
                cmd = cmd1+cmd2+cmd3
		print cmd
                start_time = time.time()
                os.system(cmd)
                end_time = time.time()
                tfile.write(benchmark + ' ' + pad + ' ' + sp_seed + ' ' + fs_seed + ' ' + nop_seed + ' ' + str(nop) + ' ' +str(end_time-start_time)+'\n')
tfile.close()
