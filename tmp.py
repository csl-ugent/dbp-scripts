import os, commands
# SPEC CPU 2006 Benchmark List (Diablo compatible)
benchmark_list = ['403.gcc','400.perlbench','401.bzip2','429.mcf','433.milc','444.namd','445.gobmk','450.soplex','453.povray','456.hmmer','458.sjeng','462.libquantum','464.h264ref','470.lbm','471.omnetpp','473.astar','482.sphinx3','483.xalancbmk','998.specrand']
# first fetch the seeds from random.log
rLogPath = '/home/mohit/updated-dBp/log/random.txt'
rLog = open(rLogPath,'r')
lines = rLog.readlines()
rList = []
k = 1
for line in lines:
   value = int(line.strip('\n'))
   rList.append(value)
   print(str(k) + " - " +(str(value)))
   k = k + 1
rLog.close()

#os.system('mkdir -p /home/mohit/updated-dBp/symfiles/no-fp/8/no-fs/')
os.system('rm -rf  /home/mohit/updated-dBp/symfiles/no-fp/8/fs*')


for j in range(0,30):
    sp_seed = rList[3*j]
    fs_seed = rList[3*j+1]


    os.system('mkdir -p /home/mohit/updated-dBp/symfiles/no-fp/8/fs/'+str(fs_seed)+'/')

