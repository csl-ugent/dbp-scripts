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
REPLAY_ROOT = '/home/mohit/updated-dBp/NOPReplayOutput/no-fp/'
mkdir = "/home/mohit/dBp/new-NOP-Patches/"

tfile = open('/home/mohit/updated-dBp/Patches/nop-patching-timing.txt', 'w')
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
	    os.system('mkdir -p ' + patchPath)
		#binary = name+"-"+shuffling+"-"+nop+"-"+nopinsertionseed
		#nopinsertionlist_file = binary+"-"+fp+"-spec2006-"+pad+"-O"+opt+"-"+padseed
	    #base_file = open(nop_replay_root+"/"+name+"-"+shuffling+"-"+nop+"-"+nopinsertionseed+"-"+fp+"-spec2006-8"+"-O"+opt+"-"+padseed).readlines()
		#base_file = open(nop_replay_root+"/O"+str(opt)+"-"+name+"-"+str(8)+"-"+str(seed)+"-"+str(nop)+"-"+str(nopinsertionseed)).readlines()
		#div_file = open(nop_replay_root+name+"/O"+str(opt)+"-"+name+"-"+str(256)+"-"+str(seed)+"-"+str(nop)+"-"+str(nopinsertionseed)).readlines()
	    #div_file = open(nop_replay_root+"/"+name+"-"+shuffling+"-"+nop+"-"+nopinsertionseed+"-"+fp+"-spec2006-256"+"-O"+opt+"-"+padseed).readlines()
	#os.system("rm -f "+mkdir+name+"-"+shuffling+"-"+nop+"-"+nopinsertionseed+"-"+fp+"-O"+opt+"-"+padseed)
	    basePath = REPLAY_ROOT + '8/fs/' + fs_seed + '/' + nop_seed + '/' + chance + '/' + name + '/nopsinsertion.list'
	    divPath  = REPLAY_ROOT + '256/' + sp_seed + '/fs/' + fs_seed + '/' + nop_seed + '/' + chance + '/' + name + '/nopsinsertion.list'
	    baseFile = open(basePath,'r')
	    divFile  = open(divPath, 'r')
	    baseLines = baseFile.readlines()
	    divLines  = divFile.readlines()
	    start_time = time.time()

	    print ""
	    print "==================="
	    print "Diffing Original " + basePath
	    print "Diffing Modified " + divPath
	    print "Output file: " + patchPath + '/nop.patch'

            pFile = open(patchPath + '/nop.patch',"w")
	    n = len(baseLines)
            m = len(divLines)
            offset = 0
            prev_addr = 0
            #print divPath
            if not n == m:
                print "Oops! length of files not equal. Assumption broken."

            else:
                pFile.write(nop_seed + " " + chance + " ")
            #addr_cur_base = base_file[0].strip('\n').split(' ')[-1]
            #addr_cur_div = div_file[0].strip('\n').split(' ')[-1]
                base = baseLines[0].strip('\n').split(' ')
                #addr_cur_base = base_file[i].strip('\n').split(' ')[-1]
                addr_cur_base = base[len(base)-1]
                div = divLines[0].strip('\n').split(' ')
                #addr_cur_div = div_file[i].strip('\n').split(' ')[-1]
                addr_cur_div = div[len(div)-1]
                prev_offset = int(addr_cur_div,16)-int(addr_cur_base,16)
                pFile.write(addr_cur_base+" "+hex(prev_offset)+"\n")
                for i in range(1,n):
            	    base = baseLines[i].strip('\n').split(' ')
                #addr_cur_base = base_file[i].strip('\n').split(' ')[-1]
                    addr_cur_base = base[len(base)-1]
                    div = divLines[i].strip('\n').split(' ')
                #addr_cur_div = div_file[i].strip('\n').split(' ')[-1]
                    addr_cur_div = div[len(div)-1]
                    cur_offset = int(addr_cur_div,16)-int(addr_cur_base,16)
                    if cur_offset != prev_offset:
                        prev_offset = cur_offset
                        pFile.write(addr_cur_base+" "+hex(cur_offset)+"\n")
            pFile.close()
	    end_time = time.time()
	    tfile.write(benchmark + ' ' + sp_seed + ' ' + fs_seed + ' ' + nop_seed + ' ' + chance + ' ' + str(end_time-start_time) + '\n')
            os.system("cat " + patchPath + "/nop.patch" + " | sed \'s/0x//g\' > " + patchPath + "/opt-nop.patch" )
        #os.system("cat "+mkdir+name+"-"+nop+" | sed \"s/0x//g\" > "+mkdir1+name+"-"+shuffling+"-"+nop+"-"+nopinsertionseed+"-"+fp+"-O"+opt+"-"+padseed)
tfile.close()

