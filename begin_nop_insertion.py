import os
import sys
import time
import thread

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

p1 = "/home/mohit/diablo-source/mishra/build-Release/diablo-arm-nop -Z -kco -exidx --no-merge-exidx --nopinsertionchance "
p2 = " --nopinsertionseed "

index = 0
for benchmark in benchmarkList:
    print str(index) + ": " + benchmark
    index += 1
print ('---------------------------------------')
#benchmarkIndex = int(raw_input("Enter Benchmark Index: "))
#tfile = open('/home/mohit/updated-dBp/Patches/nopinsertion-release-build-' + str(benchmarkIndex) + '.txt','w')

benchmarkIndex = 4
for (benchmarkIndex, benchmark) in enumerate(benchmarkList):
    if benchmarkIndex <= 3:
	continue
    tfile = open('/home/mohit/updated-dBp/Patches/nopinsertion-release-build-' + str(benchmarkIndex) + '.txt','w')
#for benchmark in benchmarkList:
    for j in range(0, 30):
        sp_seed = str(rList[3*j])
        fs_seed = str(rList[3*j+1])
        nop_seed = str(rList[3*j+2])
        for chance in nopChance:
	    name = benchmark.split('.')[1]
            if benchmark == "482.sphinx3":
                name = "sphinx_livepretend"
            if benchmark == "483.xalancbmk":
                name = "Xalan"
	    for pad in stackpad:
                # benchmark's path
                b = "/home/mohit/updated-dBp/build/no-fp"
                # nop lists path
                nopListsPath = "/home/mohit/updated-dBp/NOPInsertionLists/no-fp/"

                if pad == '256':
                    b = b + "/256/" + sp_seed + "/fs/"+fs_seed+"/"+benchmark
                    nopListsPath = nopListsPath + "/256/" + sp_seed + "/fs/"+fs_seed+"/"+"/"+nop_seed+"/"+name
                else:
                    b = b + "/8/fs/"+fs_seed+"/"+benchmark
                    nopListsPath = nopListsPath + "/8/fs/"+fs_seed+"/"+"/"+nop_seed+"/"+name

		print (benchmark + ' ' + str(pad) + ' ' + str(sp_seed) + ' ' + str(fs_seed) + ' ' + str(nop_seed) + ' ' + ' ' + str(chance))
#		dummy = raw_input("Enter to continue ...")
		print ('Making a copy of benchmark...')
	        os.system('sudo cp ' + b + '/' + name +' ' + b + '/' + name + '-' + nop_seed + '-' + chance)
		print('Generating correct map file for the binary to be passed to diablo...')
		os.system('sudo egrep -v \'mohit.bjorn\' ' + b + '/' + name + '.map > ' + b + '/' + name + '-' + nop_seed + '-' + chance + '.map') 
		nopChancePath = nopListsPath + "/"+chance
		os.system('sudo mkdir -p ' + nopChancePath)
		cmd1 = "cd " + b + ";"
		# begin nop insertion then
		binaryName = name  + "-" + nop_seed + "-" + chance
		cmd2 = "sudo " + p1 + chance + " " + binaryName + " --nopinsertionseed " + nop_seed + ";"
		# mv b.out.list to NOPInsertionLists folder with correct path defined
		cmd3 = "sudo mv b.out.list " + nopChancePath +  "/" + ";"
		# mv b.out to NOPInsertionLists folder with correct path defined
		cmd4 = "sudo mv b.out " + nopChancePath + "/" + ";"
		# mv nopsinsertion.list to correct path as above
		cmd5 = "sudo mv nopsinsertion.list " + nopChancePath + "/" + ";" 
		# executecmd1 through cmd4 wrapper in a single os.system command, else the call becomes async, which is not wanted
		cmd = cmd1 + cmd2 + cmd3 +cmd4 + cmd5
                start_time = time.time()
                os.system(cmd)
                end_time = time.time()
	
                tfile.write(benchmark + ' ' + str(pad) + ' ' + str(sp_seed) + ' ' + str(fs_seed) + ' ' + str(nop_seed) + ' ' + ' ' + str(chance) + ' ' + str(end_time-start_time)+'\n')

    tfile.close()
