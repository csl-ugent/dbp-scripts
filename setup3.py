'''
Prepare for function shuffling
- extract objects recursively
- extract text sections from the objects
- setup4.py will shuffle the sections
'''


import os, sys, commands
benchmarkList = ['403.gcc','400.perlbench','401.bzip2','429.mcf','433.milc','444.namd','445.gobmk','450.soplex','453.povray','456.hmmer','458.sjeng','462.libquantum','464.h264ref','470.lbm','471.omnetpp','473.astar','482.sphinx3','483.xalancbmk','998.specrand']

'''
What do we have to store?
- disassemble each object (only headers) and store them in individual object file
- combine all the headers into one file 
- extract text-sections of each objects into one file

/tmp/func-shuffling/
		   disassemble/
			     benchmark/objects/
			     benchmark/combined/benchmark
		   text-sections/
				benchmark
		   objects/benchmark
'''



root = '/home/mohit/updated-dBp/tmp/func-shuffling/'
disassemblePath = root + 'disassemble/'
textSectionsPath =  root + 'text-sections/'
objectsPath = root + 'objects/'

if os.path.exists(root):
    os.system('rm -rf ' + root)
os.system('mkdir -p ' + root)
os.system('mkdir -p ' + textSectionsPath)

# construct command for objdump 
objdump_part1 = '/home/mohit/diablo/arm-linux/gcc-4.8.1/bin/arm-diablo-linux-gnueabi-objdump -h '
objdump_part2 = ' | grep \"\.text\.\" | egrep -v \"\.ARM\.\" >> ' + disassemblePath 

os.system('mkdir -p ' + objectsPath)

for benchmark in benchmarkList:
   	os.system('mkdir -p ' + disassemblePath + benchmark + '/objects/')
	os.system('mkdir -p ' + disassemblePath + benchmark + '/combined/')




	 # find all object files for a benchmark
        print('************************* ' + benchmark + '**********************')
	
	benchmarkPath = '/home/mohit/updated-dBp/build/no-fp/8/no-fs/'+benchmark

	findObjParam = ' -type f -name \*.o '
	pathObj = objectsPath + benchmark

	os.system('touch  ' + pathObj)

	# extract all the objcct files recursively and store them pathObj*
	print('\t\tfinding objects ...')
	commands.getoutput('find ' + benchmarkPath + findObjParam + ' >> ' + pathObj)
	objFile = open(pathObj,'r')
	readObjFile = objFile.readlines()
	objFile.close()
	print('\t\tfound and extracted.')
	print ('\t=============================================')
	

	'''
	Once you have found the objects within the benchmark,
	start extracting the text sections of all the objects.
	These text sections will then be shuffled.
	'''
        
	
	# do for all objects in a benchmark
	
	for o in readObjFile:
	    o = o.strip('\n')
	    '''
	    o will be like /home/mohit/updated-dBp/tmp/func-shuffling/objects/401.bzip2/blabla.o
	    we want to extract only blabla.o now
	    '''
	    objList = filter(None, o.split('/'))[8:]
	    obj = '?'.join(objList)
	    print(obj)
	    
	    dumpHeaders = disassemblePath +  benchmark + '/' + obj
	    os.system('touch ' + dumpHeaders)
	    commands.getoutput(objdump_part1 + o + objdump_part2 + benchmark + '/objects/' + obj)
	    commands.getoutput('sed -i \'s/^ //\' ' + dumpHeaders)	    
	    print('\t\t objdump -h ' + o + ' completed')
	    ##################################################

	'''
	prepare the text sections now for passing them to setup4.py to shuffle them
	'''

	
	textSections = open(textSectionsPath + benchmark, 'w')
	combinedDisassemble = open(disassemblePath + benchmark + '/combined/' + benchmark, 'w')
	
	for o in readObjFile:
	    o = o.strip('\n')
	    '''
            o will be like /home/mohit/updated-dBp/tmp/func-shuffling/objects/401.bzip2/blabla.o
            we want to extract only blabla.o now
            '''
            objList = filter(None, o.split('/'))[8:]
            obj = '?'.join(objList)
	    headersFile = open(disassemblePath + benchmark + '/objects/' + '/' + obj,'r')
	    readHeaders = headersFile.readlines()
	    headersFile.close()
	    for header in readHeaders:
		combinedDisassemble.write(header)
		header = filter(None, header.strip('\n').split(' '))
		textSections.write('\t'+'/'.join(obj.split('?'))+' ('+header[1]+' .mohit.bjorn)\n')
	combinedDisassemble.close()
	textSections.close()		
