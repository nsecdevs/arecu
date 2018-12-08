#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''Arecu - Android Application Reverse Engineering Commandline Utility

Arecu is reverse engineering tool fot Android applications.

- Decompile the apk file using JavaDecompiler
- Decompile the apk file using Procyon Decompiler

'''

from logging import getLogger, StreamHandler, DEBUG
import argparse
import os
import shutil
import zipfile
import modules
import sys
import subprocess

### Configuration ###
TMP_DIR = '/tmp/arecu_tmp'
TOOLS_PATH = '/usr/local/bin/arecu_dir'
VERSION = '1.0.0'

### Make Parser ###
parser = argparse.ArgumentParser(
        prog = 'Arecu',
        usage = 'arecu [options...] <apk_file>',
        description = 'Arecu is reverse engineering tool for apk.',
        epilog = 'Copyright (C) 2018 Nao Komatsu',
        add_help = True
        )

parser.add_argument('apk_file',
        help = 'Target apk file.'
        )

parser.add_argument('-j', '--jdcmd',
        help = 'Decompile the apk file using JavaDecompiler.',
        action = 'store_true',
        default = False
        )

parser.add_argument('-p', '--procyon',
        help = 'Decompile the apk file using Procyon Decompiler',
        action = 'store_true',
        default = False
        )

parser.add_argument('-o', '--outdir',
        help = 'The name of directory that gets written. Default is current directory.',
        type = str,
        default = '.')

parser.add_argument('--version',
        version = '%(prog)s version ' + VERSION,
        action = 'version',
        default = False
        )

### Logging Configuration ###
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)
logger.propagate = False

def mkdir(dir):
    logger.debug('--- Make temprary directory ---')
    logger.debug(dir)
    os.makedirs(dir, exist_ok = True)

def rmdir(dir):
    logger.debug('--- Remove temporary directory ---')
    logger.debug(dir)
    shutil.rmtree(dir)

def unzip(file, outdir):
    logger.debug('--- Unzip apk file ---')
    with zipfile.ZipFile(file) as existing_zip:
        existing_zip.extractall(outdir)

def d2j(file, outfile):
    logger.debug('--- Dex to Jar ---')
    subprocess.run([TOOLS_PATH + '/dex2jar/d2j-dex2jar.sh', file, '-o', outfile])

def jdcmd(file, outdir):
    logger.debug('--- JavaDecompiler ---')
    subprocess.run([TOOLS_PATH + '/jd-cmd/jd-cli', '-od', outdir, file])

def procyon(file, outdir):
    logger.debug('--- Procyon Decompiler ---')
    subprocess.run(['java', '-jar', TOOLS_PATH + '/procyon/procyon.jar', '-jar', file, '-o', outdir])

def main():
    # Analysis argument
    args = parser.parse_args()
    apk = args.apk_file
    basename = os.path.basename(apk)
    name, ext = os.path.splitext(basename)
    outdir = args.outdir + '/' + name

    # print('Target apk: ' + apk)
    # print('basename: ' + basename)
    # print('name: ' + name)
    # print('ext: ' + ext)
    # print('outdir: ' + outdir)

    # Decompile apk file
    if (args.jdcmd or args.procyon):
        mkdir(TMP_DIR)
        unzip(apk, TMP_DIR)
        d2j(TMP_DIR + '/classes.dex', TMP_DIR + '/classes.jar')

        # Using JavaDecompiler
        if (args.jdcmd):
            jdcmd(TMP_DIR + '/classes.jar', outdir + '_jdcmd')

        # Using Procyon Decompiler
        if (args.procyon):
            procyon(TMP_DIR + '/classes.jar', outdir + '_procyon')

        rmdir(TMP_DIR)

if __name__ == '__main__':
    main()