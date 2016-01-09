import os
import sys
import subprocess

def loop_len_shift(rootDir, offset):

	for dirName, subdirList, fileList in os.walk(rootDir, topdown=False):
		if dirName.endswith('Media'):	
		    fileList = [ fi for fi in fileList if fi.endswith('.aiff') ]
		    print('Found directory: %s' % dirName)
		    for fname in fileList:
				print('\t%s' % fname)	
				#subprocess.call(["sox", fname, "trim"])
				soxi = subprocess.check_output(['sox', '--info', fname], shell=True)
				print soxi

				soxi_split = sox1.split()

				#subprocess.call(['sox', fname, 'temp%1n.aiff', 'trim 0', end-offset, ': newfile : trim 0', offset])
				#subprocess.call(['sox', 'temp0.aiff', 'temp1.aiff', 'fname_new.aiff'])

				# cleanup
				#os.remove('temp0.aiff')
				#os.remove('temp1.aiff')


	return 

if __name__ == "__main__":
	print '...Time-shifting loops by ' + sys.argv[2] + ' msec...'
	loop_len_shift(sys.argv[1], sys.argv[2])  