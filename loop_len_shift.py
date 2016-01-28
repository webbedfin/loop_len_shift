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
            fileList = [fi for fi in fileList if fi.endswith('aiff')]
            print('Found directory: %s' % dirName)
            for fname in fileList:
                print('\t%s' % fname)
                soxi = subprocess.check_output(['sox', '--info', dirName + '\\' + fname], shell=True)
                # print soxi

                # find sample rate
                for line in soxi.split('\n'):
                    if re.search(r'Sample Rate', line):
                        fs = line.split()[3]
                        break
                print 'fs = ' + fs

                # find sample length
                for line in soxi.split('\n'):
                    if re.search(r'Duration', line):
                        for section in line.split('='):
                            if re.search(r'samples', section):
                                loop_len = float(section.split()[0])
                                break
                print 'loop_len = ' + str(loop_len)

                # convert offset to samples
                off_samps = int(float(offset) * float(fs) / 1000.0)
                print 'sample offset = ' + str(off_samps)

                # split name
                f = fname.split('.')
                w = f[0]
                wname = w + '.wav'

                # convert aiff to working wav
                args = [
                    'sox',
                    dirName + '\\' + fname,
                    wname
                ]
                proc = subprocess.Popen(args, shell=True)
                proc.wait()
                print proc.returncode

                # sox fname.aiff temp%1n.aiff trim 0s (loop_len-offset)s : newfile : trim 0s (offset)s
                args = [
                    'sox',
                    wname,
                    'temp%1n.wav',
                    'trim',
                    '0s',
                    str(int(loop_len - off_samps)) + 's',
                    ':',
                    'newfile',
                    ':',
                    'trim',
                    '0s',
                    str(int(off_samps)) + 's'
                ]
                proc = subprocess.Popen(args, shell=True)
                proc.wait()
                print proc.returncode

                args = [
                    'sox',
                    'temp2.wav',
                    'temp1.wav',
                     wname
                ]
                proc = subprocess.Popen(args, shell=True)
                proc.wait()
                print proc.returncode

                # convert back to aiff
                args = [
                    'sox',
                    wname,
                    #dirName + '\\' + fname
                    dirName + '\\new.aiff'
                ]
                proc = subprocess.Popen(args, shell=True)
                proc.wait()
                print proc.returncode

                # cleanup
                os.remove('temp1.wav')
                os.remove('temp2.wav')
                os.remove(wname)

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
