import os
import time

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

PATCH_PATH  = '/home/mohit/updated-dBp/Patches/no-fp/'
NOP_LIST_PATH = '/home/mohit/updated-dBp/NOPInsertionLists/no-fp/'
mkdir = "/home/mohit/dBp/new-NOP-Patches/"

tfile = open('/home/mohit/updated-dBp/Patches/nop-diff-timing.txt', 'w')
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
                continue
        if benchmark == '998.specrand':
                continue
        for chance in nopChance:
            patchPath = '/home/mohit/updated-dBp/Patches/nop/no-fp/' + sp_seed + '/'+ fs_seed + '/' + nop_seed + '/'+ chance + '/' + name
	    diffPath = NOP_LIST_PATH + '/diff/' + fs_seed + '/' + nop_seed + '/' + name + '/' + chance
            os.system('mkdir -p ' + diffPath)
                #binary = name+"-"+shuffling+"-"+nop+"-"+nopinsertionseed
                #nopinsertionlist_file = binary+"-"+fp+"-spec2006-"+pad+"-O"+opt+"-"+padseed
            #base_file = open(nop_replay_root+"/"+name+"-"+shuffling+"-"+nop+"-"+nopinsertionseed+"-"+fp+"-spec2006-8"+"-O"+opt+"-"+padseed).readlines()
                #base_file = open(nop_replay_root+"/O"+str(opt)+"-"+name+"-"+str(8)+"-"+str(seed)+"-"+str(nop)+"-"+str(nopinsertionseed)).readlines()
                #div_file = open(nop_replay_root+name+"/O"+str(opt)+"-"+name+"-"+str(256)+"-"+str(seed)+"-"+str(nop)+"-"+str(nopinsertionseed)).readlines()
            #div_file = open(nop_replay_root+"/"+name+"-"+shuffling+"-"+nop+"-"+nopinsertionseed+"-"+fp+"-spec2006-256"+"-O"+opt+"-"+padseed).readlines()
        #os.system("rm -f "+mkdir+name+"-"+shuffling+"-"+nop+"-"+nopinsertionseed+"-"+fp+"-O"+opt+"-"+padseed)
            basePath = NOP_LIST_PATH + '8/fs/' + fs_seed + '/' + nop_seed + '/' + name + '/' + chance + '/nopsinsertion.list'
            divPath  = NOP_LIST_PATH + '256/' + sp_seed + '/fs/' + fs_seed + '/' + nop_seed + '/' + name + '/' + chance + '/nopsinsertion.list'
	    start_time = time.time()
	    os.system("diff " + basePath + " " + divPath + " | egrep -v '>|<|---' > " + diffPath + "/nop.diff")
	    end_time = time.time()
	    tfile.write(name + ' ' + sp_seed + ' ' + fs_seed + ' ' + nop_seed + ' ' + chance + ' ' + str(end_time - start_time) + '\n')
tfile.close()
