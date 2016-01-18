#!/usr/bin/env python
__copyright__ = """
                        2016 by Chris Derry
"""

import os
import sys
import argparse
import subprocess
import re

def loop_len_shift(path, offset):

    for dirName, subdirList, fileList in os.walk(path, topdown=False):

        if dirName.endswith('Media'):
            fileList = [fi for fi in fileList if fi.endswith('.aiff')]
            print('Found directory: %s' % dirName)
            for fname in fileList:
                print('\t%s' % fname)
                #subprocess.call(["sox", fname, "trim"])
                soxi = subprocess.check_output(['sox', '--info', dirName + '\\' + fname], shell=True)
                print soxi

                # find sample rate
                for line in soxi.split('\n'):
                    if re.search(r'Sample Rate', line):
                        fs = line.split()[3]
                print fs        

                # find sample length 
                for line in soxi.split('\n'):
                    if re.search(r'Duration', line):
                        for section in line.split('='):
                            if re.search(r'samples',section):
                                loop_len = float(section.split()[0])
                print loop_len

                # convert offset to samples
                off_samps = float(offset)*float(fs)/1000.0
                print off_samps

                # sox fname.aiff temp%1n.aiff trim 0s (loop_len-offset)s : newfile : trim 0s (offset)s
                junkstr = 'temp%1n.aiff', 'trim 0s ' + str(int(loop_len - float(offset))) + 's : newfile : trim 0s ' + str(offset) + 's'
                
                print junkstr

                #subprocess.call(['sox', dirName + '\\' + fname, 'temp%1n.aiff', 'trim 0s ' + str(int(loop_len - float(offset))) + ' s : newfile : trim 0s' + str(offset) + 's'])
                subprocess.call(['sox', dirName + '\\' + fname, junkstr])
                #subprocess.call(['sox', 'temp0.aiff', 'temp1.aiff', 'fname_new.aiff'])

                # cleanup
                #os.remove('temp0.aiff')
                #os.remove('temp1.aiff')

    return

if __name__ == "__main__":
    #print '...Time-shifting loops by ' + sys.argv[2] + ' msec...'
    #loop_len_shift(sys.argv[1], sys.argv[2])

    """ Main entry point """

    print """
                    Loop length shift
    {0}

    """.format(__copyright__)

    # Input argument parsing
    parser = argparse.ArgumentParser(description='Looplenshift')
    parser.add_argument('path', help='Root dir or aiff')
    parser.add_argument('offset', help='Offset (ms)', default=0)
    args = parser.parse_args()

    # Check that path exists
    if os.path.isfile(args.path) is None:
        print 'Path does not exist'
        sys.exit(0)

    loop_len_shift(args.path, args.offset)
