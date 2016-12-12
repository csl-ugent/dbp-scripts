import os
import random
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

#ROOT_PATH = "/home/mohit/dBp/"+fp+"process-spec2006-"+str(opt)+"-O"+str(seed)+"/"

tfile = open('/home/mohit/updated-dBp/Patches/stackpad-time.txt','w')

for i in range(0,30):
    sp_seed = str(rList[3*i])
    fs_seed = str(rList[3*i+1])
    tfile.write('  * sp_seed = '+str(sp_seed)+' ' + ', fs_seed = ' +str(fs_seed) + '\n')
    os.system('mkdir -p ' + "/home/mohit/updated-dBp/Patches/no-fp/"+str(sp_seed)+"/"+str(fs_seed)+"/")
    for benchmark in benchmarkList:
        tfile.write('$ ' + benchmark + '\n')
        start_time = time.time()
	PATH_BASE = "/home/mohit/updated-dBp/tmp/records/no-fp/8/fs/"+str(fs_seed)+"/"+benchmark+"/"
        PATH_DIV = "/home/mohit/updated-dBp/tmp/records/no-fp/256/"+str(sp_seed)+"/fs/"+str(fs_seed)+"/"+benchmark+"/"

        RECORD_TYPE = ['MOULE', 'FILE', 'PUBLIC', 'STACK']
        # Sorting the directory listing since os.listdir lists in "arbitrary" order

        func_addr_to_name = {}
        func_name_to_addr = {}

        PATH_BASEb = PATH_BASE + "FUNC_FORMATTED_SPLIT/"
        PATH_DIVb = PATH_DIV + "FUNC_FORMATTED_SPLIT/"

        mkdir = PATH_DIV + "DIFF_PER_FUNC/"
        module_id = open(PATH_DIV+"/MODULE_RECORD").readlines()[0].strip('\n').split(' ')[-2]

        fList = os.listdir(mkdir)
        fList = [str(j) for j in sorted([int (i) for i in fList])]
        num = len(fList)
        mini = 10
        if num < mini:
            mini = num
        for i in range(mini):
            fList[i] = "0"+fList[i]

        num_func = len(fList)
        name = benchmark.split('.')[1]
        if benchmark == "482.sphinx3":
                name = "sphinx_livepretend"
        if benchmark == "483.xalancbmk":
                name = "Xalan"
        pfile = open("/home/mohit/updated-dBp/Patches/no-fp/"+str(sp_seed)+"/"+str(fs_seed)+"/"+name+".patch",'w')
        
        pfile.write("M"+module_id+"\n")
        carry = 0
        offset = 0
        '''
        # Building function DB
        fTable = open(base_path+"func-table").readlines()
        num_func = len(fTable)
        f_DB = {}
        for i in range(num_func):
            f = fTable[i].strip('\n').split(' ')
            value = []
            value.append(str(i+1))
            value.append(f[0])
            f_DB[f[1]] = value

        #print f_DB

        '''
        for f in range(1,num_func):
            line_num = 0
            f_path = mkdir+"/"+fList[f]
            #print fList[f]
            sf_base = open(PATH_BASEb+"/"+fList[f]).readlines()
            sf_div = open(PATH_DIVb+"/"+fList[f]).readlines()
            if os.stat(f_path).st_size == 0L:
                a1 = sf_base[0].strip('\n').split(' ')
                a2 = sf_div[0].strip('\n').split(' ')
                tmp = int(a2[0],16)-int(a1[0],16)
                if not tmp == int(carry):
                    carry = tmp
                    pfile.write("X"+str(carry)+"\nF"+fList[f]+"\n")
                continue
            # else, there are changes required
            #func_addr_size = int(open(PATH_DIV+"/FUNC_SPLIT/"+fList[f]).readlines()[0].split(' ')[]
            dif_file = open(f_path)
            a1 = sf_base[0].strip('\n').split(' ')
            a2 = sf_div[0].strip('\n').split(' ')
            tmp = int(a2[0],16)-int(a1[0],16)
            if not tmp == int(carry):
                carry = (tmp)
		pfile.write("X"+str(carry)+"\nF"+fList[f]+"\n")
                continue
            # else, there are changes required
            #func_addr_size = int(open(PATH_DIV+"/FUNC_SPLIT/"+fList[f]).readlines()[0].split(' ')[]
            dif_file = open(f_path)
            a1 = sf_base[0].strip('\n').split(' ')
            a2 = sf_div[0].strip('\n').split(' ')
            tmp = int(a2[0],16)-int(a1[0],16)
            if not tmp == int(carry):
                carry = (tmp)
                pfile.write("X"+str(carry)+"\n")
            pfile.write("F" + fList[f]+" \n")
            #sf_base = open(PATH_BASEb+"/"+fList[f]).readlines()
            #sf_div = open(PATH_DIVb+"/"+fList[f]).readlines()
            # iterate over the lines of the diff file

            for line in dif_file.readlines():
                line = line.strip('\n')
                # Case when 'd'
                '''
                if 'd' in line:
                    l = line.split('d')
                    delete = l[0].split(',')
                    num_deleted = len(delete)
                    pfile.write("D"+str(num_deleted)+" L"+l[0]+"\n")
                    start = int(delete[0])
                    for i in range(num_deleted):
                        deleted_line = sf_base[i+start].strip('\n')
                        #pfile.write("<"+inserted_line+"\n")
                        local_offset = deleted_line.split(' ')[0]
                        carry = carry - int(local_offset,16)
                    pfile.write("="+str(carry)+"\n")
                '''
                if 'd' in line:
                    l = line.split('d')
                    old = l[0].split(',')
                    old_n = len(old)
                    local_offset_old = 0
                    if old_n == 2:
                            old_n = int(old[1])-int(old[0])+1
                    ind_old = int(old[0])                            
                    pfile.write("D"+str(old_n)+" "+str(int(old[0])-int(line_num))+"\n")
                    for i in range(old_n):
                                #lnew = sf_div[ind_new+i].strip('\n')
                                lold = sf_base[ind_old+i].strip('\n')
#pfile.write((lnew)+"\n")
                                lold = lold.split(' ')
                                local_offset_old = local_offset_old + int(lold[0],16)
                    line_num = int(old[0])
                    carry = carry - local_offset_old
                # Case when 'a'
                elif 'a' in line:
                    #if not line == '1c1':
                        l = line.split('a')    # ['86,89' , '87,93']
                        #print l
                        old = l[0].split(',')   # old = ['86','89']
                        new = l[1].split(',')   # new = ['87','93']
                        old_n = len(old)        # old_n = 2
                        new_n = len(new)        # new_n = 2
                        if old_n == 2:
                            old_n = int(old[1])-int(old[0])+1
                        if new_n == 2:
                            new_n = int(new[1])-int(new[0])+1
                        pfile.write("A"+str(new_n)+" "+str(int(old[0])-int(line_num))+"\n")
                        line_num = int(old[0])
                        local_offset_new = 0
                        local_offset_old = 0
                        ind_new = int(new[0])
                        ind_old = int(old[0])
                        for i in range(new_n):
                            lnew = sf_div[ind_new+i].strip('\n')
                            pfile.write((lnew)+"\n")
                            lnew = lnew.split(' ')
                            local_offset_new = local_offset_new + int(lnew[0],16)

                        carry = carry + local_offset_new
                # Case when 'c'
                elif 'c' in line:
                    #if not line == '1c1':
                        l = line.split('c')    # ['86,89' , '87,93']
                        #print l
                        old = l[0].split(',')   # old = ['86','89']
                        new = l[1].split(',')   # new = ['87','93']
                        old_n = len(old)        # old_n = 2
                        new_n = len(new)        # new_n = 2
                        listlines = []
                        if old_n == 2:
                            old_n = int(old[1])-int(old[0])+1
                        if new_n == 2:
                            new_n = int(new[1])-int(new[0])+1
                        pfile.write("C"+str(old_n)+":"+str(new_n)+" "+str(int(old[0])-int(line_num))+"\n")
                        line_num = int(old[0])
                        local_offset_new = 0
                        local_offset_old = 0
                        ind_new = int(new[0])
                        ind_old = int(old[0])
                        if not old_n == new_n:
                            for i in range(new_n):
                                lnew = sf_div[ind_new+i].strip('\n')
                                #lold = sf_base[ind_old+i].strip('\n')
                                pfile.write((lnew)+"\n")
                                lnew = lnew.split(' ')
                                local_offset_new = local_offset_new + int(lnew[0],16)
                                #local_offset_old = local_offset_old + int(lold[0],16)
                            for i in range(old_n):
                                #lnew = sf_div[ind_new+i].strip('\n')
                                lold = sf_base[ind_old+i].strip('\n')
                                #pfile.write((lnew)+"\n")
                                lold = lold.split(' ')
                                local_offset_old = local_offset_old + int(lold[0],16)
                                #local_offset_old = local_offset_old + int(lold[0],16)
                        elif old_n == new_n:
                            #maplines={}
                            #k = -1
                            for i in range(old_n):
                                lnew = sf_div[ind_new+i].strip('\n')
                                lold = sf_base[ind_old+i].strip('\n')

                                fields_new = lnew.split(' ')
                                fields_old = lold.split(' ')
                                for fn in range(len(fields_new)):
                                    if fields_new[fn] == fields_old[fn]:
                                        pfile.write("  ")
                                    else:
                                        if fn == 0:
                                            pfile.write(str(int(fields_new[fn],16)-int(fields_old[fn],16))+" ")
                                        else:
                                            pfile.write(fields_new[fn])
                                pfile.write("\n")
                                #lold = lold.split(' ')
                                local_offset_old = local_offset_old + int(fields_old[0],16)
                                local_offset_new = local_offset_new + int(fields_new[0],16)
                                

                        carry = carry + local_offset_new - local_offset_old
                        #pfile.write("="+str(carry)+"\n")




        # Now patching for PUBLIC RECORDS, for this we need to refer to function DB,
        # That can be done while generating the new symbol file

        # Now consider STACK RECORDS

        pfile.write("STACK\n")
        stack_records_old = open(PATH_BASE+"/STACK_RECORD").readlines()
        stack_records_new = open(PATH_DIV+"/STACK_RECORD").readlines()
        nold = len(stack_records_old)
        nnew = len(stack_records_new)

        skip = 0
        if not nold == nnew:
            print "stack records diferent"
        else:
            i = 0
            while i < nold:
                if 'INIT' in stack_records_old[i]:
                    skip = skip + 1
                elif 'sp' in stack_records_old[i]:
                    record_old = stack_records_old[i].strip('\n').split(' ')
                    record_new = stack_records_new[i].strip('\n').split(' ')
                    if record_old[3] == record_new[3]:
                        skip = skip + 1
                    else:
                        offset = int(record_new[3]) - int(record_old[3])
                        pfile.write(str(skip)+" "+str(offset/8)+"\n")
                        skip = 0
                else:
                    skip = skip + 1
                i = i + 1
        pfile.close()
        end_time = time.time()
        tfile.write('\t time = ' + str(end_time - start_time)+'\n')
tfile.close()
