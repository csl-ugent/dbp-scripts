'''
inject the shuffled ldscript
'''
import os, subprocess
benchmarkList = ["403.gcc",'400.perlbench','401.bzip2','429.mcf','433.milc','444.namd','445.gobmk','450.soplex','453.povray','456.hmmer','458.sjeng','462.libquantum','464.h264ref','470.lbm','471.omnetpp','473.astar','482.sphinx3','483.xalancbmk','998.specrand']

# get the random seeds from random log
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

for benchmark in benchmarkList:
    for j in range(0, 30):
	sp_seed = str(rList[3*j])
	fs_seed = str(rList[3*j+1])
	print('grabbing link command...')
	tail_8 = subprocess.check_output('tail -n 1 /home/mohit/updated-dBp/build/no-fp/8/fs/' + fs_seed + '/' + benchmark + '/make.out', shell=True)
	print(tail_8)
	tail_8 = tail_8.strip('\n')
	tail_256 = subprocess.check_output('tail -n 1 /home/mohit/updated-dBp/build/no-fp/256/' + sp_seed + '/fs/' + fs_seed + '/' + benchmark + '/make.out', shell=True)
        tail_256 = tail_256.strip('\n')

	name = benchmark.split('.')[1]
	if benchmark == '482.sphinx3':
	    name = 'sphinx_livepretend'
	if benchmark == '483.xalanbmk':
	   name = 'Xalan'
	print('cd into benchmark build and performing function shuffling')
	print('... for stackpadding = 8 ...')
	os.system('cd /home/mohit/updated-dBp/build/no-fp/8/fs/' + fs_seed + '/' + benchmark + ';' + tail_8 + ' -Wl,-T /home/mohit/updated-dBp/tmp/func-shuffling/shuffled-sections/' + fs_seed + '/' + benchmark + '.xc')
	print('... for stackpadding = 256 ...')
	os.system('cd /home/mohit/updated-dBp/build/no-fp/256/' + sp_seed + '/fs/' + fs_seed + '/' + benchmark +';'+tail_256 + ' -Wl,-T /home/mohit/updated-dBp/tmp/func-shuffling/shuffled-sections/' + fs_seed + '/' + benchmark + '.xc')


