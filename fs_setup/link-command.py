import subprocess, os
benchmark_list = ["403.gcc",'400.perlbench','401.bzip2','429.mcf','433.milc','444.namd','445.gobmk','450.soplex','453.povray','456.hmmer','458.sjeng','462.libquantum','464.h264ref','470.lbm','471.omnetpp','473.astar','482.sphinx3','483.xalancbmk','998.specrand']
padseed = ['1']
shufseed = ['12345']
opt_level = ['s']
fp_list = ['no-fp']
for fp in fp_list:
	for pad in ['8','256']:
		for opt in opt_level:
			for ps in padseed:
				for ss in shufseed:
					for benchmark in benchmark_list:
						tail = subprocess.check_output("tail -n 1 /home/mohit/dBp/"+fp+"-spec2006-"+pad+"-O"+str(opt)+"-"+str(ps)+"/"+benchmark+"/make.out", shell=True)
						tail = tail.strip('\n')
						name = benchmark.split('.')[1]
						if benchmark == "482.sphinx3":
								name = "sphinx_livepretend"
						if benchmark == "483.xalancbmk":
									name = "Xalan"
						#if stackpad == '256':
						os.system("cd /home/mohit/dBp/"+fp+"-spec2006-"+pad+"-O"+str(opt)+"-"+str(ps)+"/"+benchmark+";"+tail+" -Wl,-T /home/mohit/dBp/function-shuffling/shuffled-"+pad+"/"+benchmark.split('.')[-1]+"-"+ss+".xc")
						os.system("cp "name+" "+name+"-"+ss)
						#else:
							#os.system("cd /home/mohit/dBp/function-shuffling/spec2006-"+stackpad+"/"+benchmark+";"+tail)
