import os
import time

benchmarkList =['400.perlbench','401.bzip2','429.mcf','433.milc','444.namd','445.gobmk','450.soplex','453.povray','456.hmmer','458.sjeng','462.libquantum','464.h264ref','470.lbm','471.omnetpp','473.astar','482.sphinx3','483.xalancbmk','998.specrand', '403.gcc']
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

tfile = open('/home/mohit/updated-dBp/Patches/nop-patch-timing.txt', 'w')
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
	    start_time = time.time()
	    baseFile = open(NOP_LIST_PATH + '8/fs/' + fs_seed + '/' + nop_seed + '/' + name + '/' + chance + '/nopsinsertion.list')
	    divFile = open(NOP_LIST_PATH + '256/' + sp_seed + '/fs/' + fs_seed + '/' + nop_seed + '/' + name + '/' + chance + '/nopsinsertion.list')
	    baseLines = baseFile.readlines()
	    divLines = divFile.readlines()
            patchPath = '/home/mohit/updated-dBp/Patches/nop/no-fp/' + sp_seed + '/'+ fs_seed + '/' + nop_seed + '/'+ chance + '/' + name
            os.system('mkdir -p ' + patchPath)
	    pfile = open(patchPath + '/nop.patch', 'w')
	    diffPath = NOP_LIST_PATH + '/diff/' + fs_seed + '/' + nop_seed + '/' + name + '/' + chance + '/nop.diff'
	    diffFile = open(diffPath, 'r')
	    diffLines = diffFile.readlines()
	    last_saved_line = 0
	    carry = 0
	    for line in diffLines:
		# Case 1: if needed to delete lines
		if 'd' in line:	
		    l = line.split('d')
		    base = filter(None, l[0].split(','))
		    base_start = int(base[0])
		    num_lines_deleted = 1
		    local_offset_base = 0
		    if len(base) == 2:
			base_end = int(base[1])
			num_lines_deleted = base_end - base_start + 1
		    offset_from_last_saved_line = base_start - last_saved_line 
		    pfile.write('D' + str(offset_from_last_saved_line) + ':' + str(num_lines_deleted) + '\n')
		    last_line_saved = base_start
		    '''
		    # Compute negative carry offset
		    for i in range(num_lines_deleted):
			block_l = baseLines[base_start - 1 + i].strip('\n')
			# fetch address and instruction size
			block_info = filter(None, block_l.split(','))
			addr = block_info[0]
			ins_size = int(block_info[1]) * 4
			local_offset_base += int(ins_size)
		    carry -= local_offset_base
		    pfile.write('=' + str(carry) + '\n')
		    '''
		# Case 2: if needed to add lines
		elif 'a' in line:
		    l = line.strip('\n').split('a')
		    base = l[0].split(',')   
		    div = l[1].split(',')
		    base_start = int(base[0])
		    div_start = int(div[0])
		    div_end = div_start
		    num_lines_added = 1
		    if len(div) == 2:
			div_end = int(div[1])
			num_lines_added = div_end - div_start + 1
		    offset_from_last_saved_line = base_start - last_saved_line
		    pfile.write('A'+ str(offset_from_last_saved_line) + ':' + str(num_lines_added) + '\n')
		    last_saved_line = base_start
		    local_offset_base = 0
		    block_l = divLines[div_start - 1].strip('\n')
		    block_info = filter(None, block_l.split(','))
		    prev_ins_size = int(block_info[1])
		    count = 0
		    for i in range(num_lines_added):
			#pfile.write(divLines[div_start - 1 + i])
		        block_l = divLines[div_start - 1 + i].strip('\n')
		    	# fetch address and instruction size
                        block_info = filter(None, block_l.split(','))
                        addr = block_info[0]
                        ins_size = int(block_info[1])
			if ins_size == prev_ins_size:
			    count += 1
			    if i == num_lines_added - 1:
				pfile.write(str(count) + ',' + str(ins_size) + '\n')
			else:
			    pfile.write(str(count) + ',' + str(prev_ins_size) + '\n')
			    count = 1
			    prev_ins_size = ins_size
			    if i == div_lines_changed - 1:
                                pfile.write(str(count) + ':' + str(prev_ins_size) + '\n')
		# Case 3: replacement
		else:
		    l = line.strip('\n').split('c')
		    base = l[0].split(',')
		    div = l[1].split(',')
		    base_start = int(base[0])
		    base_end = base_start
		    div_start = int(div[0])
		    div_end = div_start
		    base_lines_changed = 1
		    div_lines_changed = 1
		    if len(base) == 2:
			base_end = int(base[1])
			base_lines_changed = base_end - base_start + 1
		    if len(div) == 2:
			div_end = int(div[1])
			div_lines_changed = div_end - div_start + 1
		    offset_from_last_saved_line = base_start - last_saved_line
		    pfile.write('C' + str(base_lines_changed) + ':' + str(div_lines_changed) + ' ' + str(offset_from_last_saved_line) + '\n')
		    last_saved_line = base_start 
		    if base_lines_changed != div_lines_changed:
			block_l = divLines[div_start - 1].strip('\n')
			block_info = block_l.split(',')
			prev_ins_size = int(block_info[1])
			count = 0
			for i in range(div_lines_changed):
			    div_l = divLines[div_start - 1 + i].strip('\n').split(',')
			    div_block_addr = int(div_l[0], 16)
			    div_block_ins = int(div_l[1])
			    if prev_ins_size == div_block_ins:
				count += 1
				if i == div_lines_changed - 1:
				    pfile.write(str(count) + ':' + str(prev_ins_size) + '\n')
			    else:
				pfile.write(str(count) + ':' + str(prev_ins_size) + '\n')
				count = 1
				prev_ins_size = div_block_ins
			        if i == div_lines_changed - 1:
                                    pfile.write(str(count) + ':' + str(prev_ins_size) + '\n')
			'''
			last_div_block = divLines[div_start - 1 + div_lines_changed - 1].strip('\n').split(',')
			last_base_block = baseLines[base_start - 1 + base_lines_changed - 1].strip('\n').split(',')
			addr_offset = int(last_div_block[0], 16) - int(last_base_block[0], 16)
			ins_offset = 4 * (int(last_div_block[1]) - int(last_base_block[1]))
			carry = addr_offset + ins_offset
			pfile.write('=' + str(carry))
			'''
		    else:
			for i in range(base_lines_changed):
			    base_l = baseLines[base_start - 1 + i].strip('\n').split(',')
			    div_l = divLines[div_start - 1 + i].strip('\n').split(',')
			    base_block_addr = int(base_l[0], 16)
			    div_block_addr = int(div_l[0], 16)
			    offset_div_addr = div_block_addr - (base_block_addr + carry)
			    offset_addr_flag = False
			    if offset_div_addr != 0:
				offset_addr_flag = True
				pfile.write(str(i+1) + ':' + str(offset_div_addr))
			    base_block_ins = int(base_l[1])
			    div_block_ins = int(div_l[1])
			    offset_ins = div_block_ins - base_block_ins
			    if offset_ins != 0:
				if offset_addr_flag == True:
				    pfile.write('O' + str(offset_ins))
				else:
				    pfile.write(str(i+1) + 'O' + str(offset_ins)) 
			   # carry += offset_div_addr + offset_ins * 4
			   # pfile.write('=' + str(carry))
			    pfile.write('\n')
	    divFile.close()
	    baseFile.close()
	    pfile.close()
	    end_time = time.time()
	    tfile.write(name + ' '+ sp_seed + ' ' + fs_seed + ' ' + nop_seed + ' ' + chance + ' ' + str(end_time - start_time)+ '\n')
tfile.close()
