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

# bpm guess range
low_bpm = 70.0
high_bpm = 140.0


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
                    if re.search(r'samples', line):
                        loop_len = int(line.split()[4])
                        break

                loop_len_s[w] = float(loop_len) / float(fs)

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

            # find the fundamental loop
            loop_len_min = 9999
            for w in loop_len_s:
                loop_len_min = min(loop_len_min, loop_len_s[w])

            print 'fs = ' + fs + 'Hz. offset = ' + str(offset_samps[w]) + ' samples'

            # check that all loops are multiples of the fundamental
            for w in loop_len_s:
                multiplier = float(loop_len_s[w]) / float(loop_len_min)
                print '\t\'' + w + '\' - ' + str(multiplier) + 'x' + ', length = ' + str(loop_len_s[w]) + 's'
                if loop_len_s[w] % loop_len_min > epsilon:
                    print fname + ' is not integer multiple! ratio = ' + str(float(loop_len_s[w]) / float(loop_len_min))

            '''        
            # guess the bpm
            lpm = 60.0 / float(loop_len_min)
            bpm_guess = 0

            for b in range(int(low_bpm), int(high_bpm)):
                q = 60.0 / float(b)
                bpm_quant = int(float(b) / q)
                l_mult = lpm / q
                z = (b / q) / l_mult
                
                """
                print '\nlpm = %f' % lpm
                print 'b = %d' % b
                print 'q = %f' % q
                print 'b/q = %f' % (b / q)
                print 'bpm_quant = %d' % bpm_quant
                print 'l_mult = %f' % l_mult
                print '(b / q) / l_mult = %f' % z
                """

                if (z == int(z)):
                    bpm_guess = b / q
                    break
            print 'bpm guess = %d' % bpm_guess
            '''
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
