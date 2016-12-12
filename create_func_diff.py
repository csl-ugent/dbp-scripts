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

benchmarkList =["403.gcc",'400.perlbench','401.bzip2','429.mcf','433.milc','444.namd','445.gobmk','450.soplex','453.povray','456.hmmer','458.sjeng','462.libquantum','464.h264ref','470.lbm','471.omnetpp','473.astar','482.sphinx3','483.xalancbmk','998.specrand']

def create_func_diff(benchmark, tfile):
    for j in range(0, 30):
        sp_seed = rList[3*j]
        fs_seed = rList[3*j+1]
        tfile.write('  * sp_seed = '+str(sp_seed)+' ' + ', fs_seed = ' +str(fs_seed) + '\n')
        print ('  * sp_seed = '+str(sp_seed)+' ' + ', fs_seed = ' +str(fs_seed) + '\n')
        PATH_DIV = "/home/mohit/updated-dBp/tmp/records/no-fp/256/"+str(sp_seed)+"/fs/"+str(fs_seed)+"/"+benchmark
        PATH_BASE = "/home/mohit/updated-dBp/tmp/records/no-fp/8/fs/"+str(fs_seed)+"/"+benchmark

        mkdir = PATH_DIV + "/DIFF_PER_FUNC"

        fList_base = os.listdir(PATH_BASE+"/FUNC_FORMATTED_SPLIT/")
        fList_div  = os.listdir(PATH_DIV+"/FUNC_FORMATTED_SPLIT/")

        fList_base = [str(j) for j in sorted([int (i) for i in fList_base])]
        fList_div  = [str(j) for j in sorted([int (i) for i in fList_div])]
        num = len(fList_base)
        mini = 10
        if num < mini:
            mini = num
        for j in range(mini):
            fList_base[j] = "0"+fList_base[j]
            fList_div[j] = "0"+fList_div[j]

        num_func = len(fList_base)
        os.system("mkdir "+mkdir)

        start_time = time.time()

        for f in range(num_func):
            dif1 = "bash -c \'diff <(tail -n +2 "+PATH_BASE+"/FUNC_FORMATTED_SPLIT/"+fList_base[f]+") "

            dif2 =  "<(tail -n +2 "+PATH_DIV+"/FUNC_FORMATTED_SPLIT/"+fList_div[f]+") "
            #dif2 =  PATH_DIV+"/FUNC_FORMATTED_SPLIT/"+fList_div[f]+" "
            grep = "| grep -v \">\|<\|---\" > "
            os.system(dif1 + dif2 + grep + mkdir+"/"+fList_div[f]+"\'")

        end_time = time.time()
        tfile.write('\ttime = ' + str(end_time - start_time) + '\n')
	print('\ttime = ' + str(end_time - start_time) + '\n')
try:
    tfile = open("/home/mohit/updated-dBp/Patches/func-diff-time.txt","w")
    for benchmark in benchmarkList:
        print('$ ' + benchmark + '\n')
        tfile.write('$ ' + benchmark + '\n')
        create_func_diff(benchmark, tfile)
        tfile.write('\n\n')
finally:
    tfile.close()
