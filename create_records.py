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

benchmarkList =['400.perlbench','401.bzip2','429.mcf','433.milc','444.namd','445.gobmk','450.soplex','453.povray','456.hmmer','458.sjeng','462.libquantum','464.h264ref','470.lbm','471.omnetpp','473.astar','482.sphinx3','483.xalancbmk','998.specrand', '403.gcc']

def create_records_for_benchmark(benchmark, stackpad, tfile):
    print (benchmark, stackpad)
    for j in range(0, 30):
	print ('Iteration #' + str(j))
	#raw_input("Press Enter to continue...")	
        sp_seed = rList[3*j]
        fs_seed = rList[3*j + 1]
        tfile.write('  * sp_seed = '+str(sp_seed)+' ' + ', fs_seed = ' +str(fs_seed) + '\n')
        name = benchmark.split('.')[1]
        if benchmark == "482.sphinx3":
                    name = "sphinx_livepretend"
        if benchmark == "483.xalancbmk":
                    name = "Xalan"
        PATH = ''
        SYM_FILE = ''

        if stackpad == 8:
            PATH = "/home/mohit/updated-dBp/tmp/records/no-fp/8/fs/"+str(fs_seed)+"/"+benchmark
            SYM_PATH = "/home/mohit/updated-dBp/symfiles/no-fp/8/fs/"+str(fs_seed)+"/"+name+".symfile"
        else:
            PATH = "/home/mohit/updated-dBp/tmp/records/no-fp/256/"+str(sp_seed)+"/fs/"+str(fs_seed)+"/"+benchmark
            SYM_PATH = "/home/mohit/updated-dBp/symfiles/no-fp/256/"+str(sp_seed)+"/fs/"+str(fs_seed)+"/"+name+".symfile"

        os.system('mkdir -p ' + PATH)

        start_time = time.time()

        # create the records file from the symfile
        os.system("less "+SYM_PATH + " | grep \"MODULE\" > "+PATH+"/MODULE_RECORD")
        os.system("less "+SYM_PATH + "  | grep \"STACK\" | sed \"s/STACK CFI //\"> "+PATH+"/STACK_RECORD")
        os.system("less "+SYM_PATH + "  | grep \"PUBLIC\" > "+PATH+"/PUBLIC_RECORD")
        os.system("less "+SYM_PATH + "  | grep -v \"MODULE\\|FILE\\|STACK\\|PUBLIC\" > "+PATH+"/FUNC_RECORD")

        os.system("mkdir -p "+PATH+"/FUNC_SPLIT")
        os.system("csplit -f "+PATH+"/FUNC_SPLIT/ "+PATH+"/FUNC_RECORD \"/FUNC/\" \"{*}\"")

        fList = (os.listdir(PATH+"/FUNC_SPLIT/"))
        fList = [str(j) for j in sorted([int(i) for i in fList])]

        os.system("mkdir "+PATH+"/FUNC_FORMATTED_SPLIT")
        num = len(fList)
        mini = 10
        if num < mini:
            mini = num
        for i in range(mini):
            fList[i] = "0"+fList[i]

        for f in fList:
            os.system("cat "+PATH+"/FUNC_SPLIT/"+"/"+f+" | cut -d \" \" -f 2,3,4 > "+PATH+"/FUNC_FORMATTED_SPLIT/"+"/"+f)
        end_time = time.time()
        tfile.write('\ttime = ' + str(end_time - start_time) + '\n')


tfile = open("/home/mohit/updated-dBp/Patches/records-creation.txt","w")
for benchmark in benchmarkList:
       print (benchmark)
       tfile.write('$ ' + benchmark + '\n')
       tfile.write('# stackpad = 8' + '\n')
       create_records_for_benchmark(benchmark, 8, tfile)
       tfile.write('# stackpad = 256' + '\n')
       create_records_for_benchmark(benchmark, 256, tfile)
       tfile.write('\n\n')
tfile.close()
