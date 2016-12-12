'''
Second Diversification - function shuffling
- First, make a copy of no-fs in fs folders as fs/<fs_seeed>/
- Perform function shuffling to the copied binaries, passing corresponding fs_seed
'''
import os
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
# Copy the binaries

for j in range(0,30):
		print('******* j = '+str(j)+' ********')
                fs_seed = rList[3*j+1]
                sp_seed = rList[3*j]
                copyFrom = "/home/mohit/updated-dBp/build/no-fp/8/no-fs/*"
                copyTo = "/home/mohit/updated-dBp/build/no-fp/8/fs/"+str(fs_seed)+"/"
		print('Copying  from ' + copyFrom + ' to ' + copyTo)
                os.system('sudo cp -a ' + copyFrom + ' ' + copyTo)
                copyFrom = "/home/mohit/updated-dBp/build/no-fp/256/"+str(sp_seed)+"/no-fs/*"
                copyTo = "/home/mohit/updated-dBp/build/no-fp/256/"+str(sp_seed)+"/fs/"+str(fs_seed)+"/"
		print('Copying from ' + copyFrom + ' to ' + copyTo)
                os.system('sudo cp -a ' + copyFrom + ' ' + copyTo)

