import os, sys, random

'''
CAUTION: When switching to with-fp, make sure you get a backup for no-fp currently executed
'''
# Generate random seeds log file
rList = []
rLogPath = '/home/mohit/updated-dBp/log/random.txt'
if os.path.exists(rLogPath):
    os.remove(rLogPath)
rLog = open(rLogPath,'a')
random.seed(101)
for i in range(1,91):
    value = (random.randint(0,1000000))
    print(value)
    rLog.write(str(value)+"\n")
    rList.append(value)
rLog.close()
# Create build directory for compiled benchmarks
for j in range(0,30):
    os.system('mkdir -p /home/mohit/updated-dBp/build/no-fp/256/' + str(rList[3*j]) + '/no-fs/')
    os.system('mkdir -p /home/mohit/updated-dBp/build/no-fp/256/' + str(rList[3*j]) + '/fs/' + str(rList[3*j+1]))

    os.system('mkdir -p /home/mohit/updated-dBp/build/no-fp/8/no-fs/')
    os.system('mkdir -p /home/mohit/updated-dBp/build/no-fp/8/fs/' + str(rList[3*j+1]))



'''
First diversification form - stackpadding
'''
# compile the benchmarks using the patched llvm
fp = "no-fp"
buildScript = "/home/mohit/intern/diabloregression/speccpu2006/"
# compile first for default binaries
install = "sudo "+buildScript+"/install.sh -r -j 6 -O \"-g -O2 -mcpu=cortex-a8 -marm -Wl,--no-demangle -Wl,--hash-style=sysv -Wl,--no-merge-exidx-entries -ffunction-sections -mllvm -stackpadding=8\" -D -d /home/mohit/updated-dBp/installed/spec2006-install-8-O2 -c arm-llvm3.6-dyn-O2 -t /home/mohit/diablo/arm-linux/gcc-4.8.1/ -p arm-diablo-linux-gnueabi -C /home/mohit/diablo-toolchains/.llvm_src/build/;"

spec2regression = "sudo "+buildScript+"/spec2regression.sh -s \"-p 917 -c blowfish mmishra@tyr\" -p /home/mohit/updated-dBp/installed/spec2006-install-8-O2 -b build_base_arm-llvm3.6-dyn-O2-nn.0000 -d /home/mohit/updated-dBp/build/no-fp/8/no-fs/"

print("************ default binraries building... **********")

os.system(install)
os.system(spec2regression)

print("\t\t done.")
# compile now for diversfiied binaries (stackpadding only)
flag = False
for j in range(0,30):
    seed = rList[3*j]
    print("*************" + str(j) +"\t" + str(seed) + "\tstarting..."+"**************")
    install = "sudo "+buildScript+"/install.sh -r -j 6 -O \"-g -O2 -mcpu=cortex-a8 -marm -Wl,--no-demangle -Wl,--hash-style=sysv -Wl,--no-merge-exidx-entries -ffunction-sections -mllvm -stackpadding=256 -mllvm -padseed="+str(seed)+"\" -D -d /home/mohit/updated-dBp/installed/spec2006-install-8-O2 -c arm-llvm3.6-dyn-O2 -t /home/mohit/diablo/arm-linux/gcc-4.8.1/ -p arm-diablo-linux-gnueabi -C /home/mohit/diablo-toolchains/.llvm_src/build/; " 
    spec2regression = "sudo "+buildScript+"/spec2regression.sh -s \"-p 917 -c blowfish mmishra@tyr\" -p /home/mohit/updated-dBp/installed/spec2006-install-8-O2 -b build_base_arm-llvm3.6-dyn-O2-nn.0000 -d /home/mohit/updated-dBp/build/no-fp/256/"+str(seed)+"/no-fs/"
    os.system(install)
    os.system(spec2regression)
    print('\t\tdone.')
    if j == 29:
	flag = True


























