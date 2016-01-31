#!/usr/bin/env python
__copyright__ = """
                      Loop length shift.
                        Shifts the start point of loops

                      Chris Derry, 2016
"""

import os
import sys
import argparse
import subprocess
import re


def loop_len_shift(path, offset):
    offset = int(offset)

    for dirName, subdirList, fileList in os.walk(path, topdown=False):
        if dirName.endswith('Media'):
            fileList = [fi for fi in fileList if fi.endswith('aiff')]
            print('\nFound directory \"%s\"' % dirName)
            loop_len_ms = dict()
            offset_ms = dict()

            for fname in fileList:
                print('\t%s' % fname)
                soxi = subprocess.check_output(['sox', '--info', dirName + '\\' + fname], shell=True)
                # print soxi

                # find sample rate
                for line in soxi.split('\n'):
                    if re.search(r'Sample Rate', line):
                        fs = int(line.split()[3])
                        break
                # print '\tfs = ' + fs

                # find sample length
                for line in soxi.split('\n'):
                    if re.search(r'Duration', line):
                        for section in line.split('='):
                            if re.search(r'samples', section):
                                loop_len = int(section.split()[0])
                                break

                loop_len_ms[fname] = float(loop_len) / 48000.0
                print '\t\tlength = ' + str(loop_len_ms[fname]) + 'ms'

                # convert offset to samples
                #offset_ms[fname] = int(float(offset) * float(fs) / 1000.0)
                offset_ms[fname] = offset * fs / 1000
                #print '\t\tsample offset = ' + str(offset_ms[fname]) + ' samples'

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
                if proc.returncode != 0:
                    print proc.returncode

                # sox fname.aiff temp%1n.aiff trim 0s (loop_len-offset)s : newfile : trim 0s (offset)s
                args = [
                    'sox',
                    wname,
                    'temp%1n.wav',
                    'trim',
                    '0s',
                    str(loop_len - offset) + 's',
                    ':',
                    'newfile',
                    ':',
                    'trim',
                    '0s',
                    str(offset_ms[fname]) + 's'
                ]

                proc = subprocess.Popen(args, shell=True)
                proc.wait()
                if proc.returncode != 0:
                    print proc.returncode

                args = [
                    'sox',
                    'temp2.wav',
                    'temp1.wav',
                     wname
                ]
                proc = subprocess.Popen(args, shell=True)
                proc.wait()
                if proc.returncode != 0:
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
                if proc.returncode != 0:
                    print proc.returncode

                # cleanup
                os.remove('temp1.wav')
                os.remove('temp2.wav')
                os.remove(wname)

                # dbg
                if os.path.isfile(dirName + '\\new.aiff'):
                    os.remove(dirName + '\\new.aiff')
                if os.path.isfile(dirName + '\\' + w + '.pkf'):
                    os.remove(dirName + '\\' + w + '.pkf')

            loop_len_min = min(loop_len_ms)


    return

if __name__ == "__main__":
    """ Main entry point """

    print """
                    Loop length shift
    {0}

    """.format(__copyright__)

    # Input argument parsing
    parser = argparse.ArgumentParser(description='Loop len shift')
    parser.add_argument('path', help='Root dir or aiff')
    parser.add_argument('offset', help='Offset (ms)', default=0)
    args = parser.parse_args()

    # Check that path exists
    if os.path.isfile(args.path) is None:
        print 'Path does not exist'
        sys.exit(0)

    print 'Time-shifting loops by ' + args.offset + ' msec...'

    loop_len_shift(args.path, args.offset)
