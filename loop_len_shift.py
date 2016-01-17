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

                # find sample length 
                for line in soxi.split('\n'):
                    if re.search(r'Dur', line):
                        for section in line.split('='):
                            if re.search(r'samples',section):
                                loop_len = section.split()[0]


                subprocess.call(['sox', fname, 'temp%1n.aiff', 'trim 0', loop_len-offset, ': newfile : trim 0', offset])
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
    parser.add_argument('offset', help='Offset', default=0)
    args = parser.parse_args()

    # Check that path exists
    if os.path.isfile(args.path) is None:
        print 'Path does not exist'
        sys.exit(0)

    loop_len_shift(args.path, args.offset)
