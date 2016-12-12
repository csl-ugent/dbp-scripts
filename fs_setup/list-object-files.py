import os, commands
# SPEC CPU 2006 Benchmark List (Diablo compatible)
benchmark_list = ['403.gcc','400.perlbench','401.bzip2','429.mcf','433.milc','444.namd','445.gobmk','450.soplex','453.povray','456.hmmer','458.sjeng','462.libquantum','464.h264ref','470.lbm','471.omnetpp','473.astar','482.sphinx3','483.xalancbmk','998.specrand']
# iterate over the default and diversified variants
for stackpad in ['8','256']:
    commands.getoutput("rm -rf /home/mohit/dBp/function-shuffling/extract-text-"+stackpad)
    commands.getoutput("mkdir -p /home/mohit/dBp/function-shuffling/extract-text-"+stackpad)
    # extract the object files information - location
    dump_text = "/home/mohit/diablo/arm-linux/gcc-4.8.1/bin/arm-diablo-linux-gnueabi-objdump -h "
    dump_text1 = " | grep \"\.text\.\" | egrep -v \"\.ARM\.\" >> /home/mohit/dBp/function-shuffling/dump-text-"+stackpad+"/"
    #commands.getoutput("rm -rf /home/mohit/dBp/function-shuffling/object-files-"+stackpad)
    commands.getoutput("mkdir -p /home/mohit/dBp/function-shuffling/object-files-"+stackpad)
    for benchmark in benchmark_list:

        #commands.getoutput("mkdir -p /home/mohit/dBp/function-shuffling/object-files-"+stackpad+"/"+benchmark)
        commands.getoutput("find /home/mohit/dBp/no-fp-spec2006-"+stackpad+"-O"+str('s')+"-"+str('1')+"/"+benchmark+" -type f -name \*.o >> /home/mohit/dBp/function-shuffling/object-files-"+stackpad+"/"+benchmark)
        ofiles = open("/home/mohit/dBp/function-shuffling/object-files-"+stackpad+"/"+benchmark).readlines()
        #commands.getoutput("rm -rf /home/mohit/dBp/function-shuffling/dump-text-"+stackpad+"/"+benchmark)
        commands.getoutput("mkdir -p /home/mohit/dBp/function-shuffling/dump-text-"+stackpad+"/"+benchmark+"/")
        obj_path_table = {}
        for f in ofiles:
            #print f
            f = f.strip('\n')
            #obj = os.path.basename(f).split('.')[0]
            path_obj = filter(None, f.split('/'))[5:]
            obj = '?'.join(path_obj)
            #path_obj = "/home/mohit/dBp/no-fp-spec2006-"+stackpad+"-O"+str('s')+"-"+str('1')+"/"+benchmark
            #if not obj in obj_path_table.keys():
            #	obj_path_table[obj]=f
            #else:
            #	print obj + " already present: "+benchmark+" - Now: "+f+" Old: "+obj_path_table[obj] 
            #print obj
            #print "Executing: "+dump_text+f+dump_text1+benchmark
            #commands.getoutput("rm -f /home/mohit/dBp/function-shuffling/dump-text"+stackpad+"/"+benchmark+"/"+obj)
            p = open("/home/mohit/dBp/function-shuffling/dump-text-"+stackpad+"/"+benchmark+"/"+obj,"w")
            p.close()
            commands.getoutput(dump_text+f+dump_text1+benchmark+"/"+obj)
            #commands.getoutput("rm -f /home/mohit/dBp/function-shuffling/dump-text/"+benchmark+"/"+obj+"-sed")
            commands.getoutput("sed -i 's/^ //' "+"/home/mohit/dBp/function-shuffling/dump-text-"+stackpad+"/"+benchmark+"/"+obj)# + " > /home/mohit/dBp/function-shuffling/dump-text/"+benchmark+"/"+obj+"-sed")
            #p = open("/home/mohit/dBp/function-shuffling/dump-text-"+stackpad+"/"+benchmark+"/"+obj,"r")
            #print p.read ()
            #p.close()
        path = "/home/mohit/dBp/function-shuffling/dump-text-"+stackpad+"/"+benchmark
        extract_path = "/home/mohit/dBp/function-shuffling/extract-text-"+stackpad+"/"+benchmark

        p = open(extract_path,"w")
        section_list = open(extract_path+"-final","w")
        for f in ofiles:
            f = f.strip('\n')
            path_obj = filter(None, f.split('/'))[5:]
            obj = '?'.join(path_obj)
            obj_sections = open(path + "/"+obj).readlines()
            for sec in obj_sections:
                section_list.write(sec)
                sec.strip('\n')
                sec = sec.split(' ')
                sec = filter(None, sec)
                #print sec
                p.write("\t"+'/'.join(obj.split('?'))+" "+"("+sec[1]+" .mohit.bjorn)\n")

                #section_list.write(obj+" "+sec[1]+" "+sec[2]+" "+sec[-1])
        p.close()
        section_list.close()


