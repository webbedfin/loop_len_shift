#!/usr/bin/env python
__copyright__ = """
                      Shifts the start point of loops.

                      Chris Derry, 2016
"""

import os
import sys
import argparse
import subprocess
import re

epsilon = 4 * sys.float_info.epsilon

def loop_len_shift(path, offset):

    for dirName, subdirList, fileList in os.walk(path, topdown=False):
        if dirName.endswith('Media'):
            fileList = [fi for fi in fileList if fi.endswith('aiff')]
            print('\n\"%s\"' % dirName)
            loop_len_s = dict()
            offset_samps = dict()

            for fname in fileList:
                # split name
                f = fname.split('.')
                w = f[0]
                wname = w + '.wav'

                soxi = subprocess.check_output(['sox', '--info', dirName + '\\' + fname], shell=True)
                # print soxi

                # find sample rate
                for line in soxi.split('\n'):
                    if re.search(r'Sample Rate', line):
                        fs = line.split()[3]
                        break

                # find sample length
                for line in soxi.split('\n'):
                    if re.search(r'Duration', line):
                        for section in line.split('='):
                            if re.search(r'samples', section):
                                loop_len = int(section.split()[0])
                                break

                loop_len_s[w] = float(loop_len) / 48000.0

                # convert offset to samples
                offset_samps[w] = int(float(offset) * float(fs) / 1000.0)

                # don't modify files if offset == 0
                if offset_samps[w] != 0:
                    # convert aiff to working wav
                    args = [
                        'sox',
                        dirName + '\\' + fname,
                        wname
                    ]
                    proc = subprocess.Popen(args, shell=True)
                    proc.wait()
                    if proc.returncode != 0:
                        raise Exception(proc.returncode)

                    # sox fname.aiff temp%1n.aiff trim 0s (loop_len-offset)s : newfile : trim 0s (offset)s
                    args = [
                        'sox',
                        wname,
                        'temp%1n.wav',
                        'trim',
                        '0s',
                        str(loop_len - offset_samps[w]) + 's',
                        ':',
                        'newfile',
                        ':',
                        'trim',
                        '0s',
                        str(offset_samps[w]) + 's'
                    ]

                    proc = subprocess.Popen(args, shell=True)
                    proc.wait()
                    if proc.returncode != 0:
                        raise Exception(proc.returncode)

                    args = [
                        'sox',
                        'temp2.wav',
                        'temp1.wav',
                        wname
                    ]
                    proc = subprocess.Popen(args, shell=True)
                    proc.wait()
                    if proc.returncode != 0:
                        raise Exception(proc.returncode)

                    # convert back to aiff
                    args = [
                        'sox',
                        wname,
                        # dirName + '\\' + fname  # destructive
                        dirName + '\\new.aiff'  # non-destructive
                    ]
                    proc = subprocess.Popen(args, shell=True)
                    proc.wait()
                    if proc.returncode != 0:
                        raise Exception(proc.returncode)

                # cleanup
                if os.path.isfile('temp1.wav'):
                    os.remove('temp1.wav')
                if os.path.isfile('temp2.wav'):
                    os.remove('temp2.wav')
                if os.path.isfile('new.aiff'):
                    os.remove(wname)

                if os.path.isfile(dirName + '\\new.aiff'):
                    os.remove(dirName + '\\new.aiff')
                if os.path.isfile(dirName + '\\' + w + '.pkf'):
                    os.remove(dirName + '\\' + w + '.pkf')

            loop_len_min = 9999
            for w in loop_len_s:
                loop_len_min = min(loop_len_min, loop_len_s[w])

            print 'fs = ' + fs + 'Hz. offset = ' + str(offset_samps[w]) + ' samples'

            for w in loop_len_s:
                multiplier = float(loop_len_s[w]) / float(loop_len_min)
                print '\t\'' + w + '\' - ' + str(multiplier) + 'x' + ', length = ' + str(loop_len_s[w]) + 's'
                if loop_len_s[w] % loop_len_min > epsilon:
                    print fname + ' is not integer multiple! ratio = ' + str()
                    print 'loop_len_ms[w] % loop_len_min = ' + str(multiplier)
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
    parser.add_argument('offset', help='Offset (ms). 0 = informational.', default=0)
    args = parser.parse_args()

    # Check that path exists
    if os.path.isfile(args.path) is None:
        print 'Path does not exist'
        sys.exit(0)

    if args.offset == '0':
        print 'Showing loop information...'
    else:
        print 'Time-shifting loops by ' + args.offset + ' msec...'

    loop_len_shift(args.path, args.offset)
