# -*- coding: utf-8 -*-

import modules
import os
import shutil
import yaml
import zipfile
from logging import getLogger

logger = getLogger('arecu').getChild('decompile')

# Configuration
with open('<YMLFILE>', 'r', encoding='utf-8') as yml:
    config = yaml.load(yml, Loader=yaml.SafeLoader)

tmp_dir = config['decompile']['tmp_dir']
lib_path = config['decompile']['lib_path']


# Decompile & Decode process
def main(args):

    # Logging
    if (args.verbose):
        level = 'DEBUG'
    else:
        level = 'INFO'
    modules.log.config(level)

    # Initialization
    logger.debug('--- Initialization ---')

    if (args.all):
        unzip = True
        jdcmd = True
        procyon = True
        apktool = True
    else:
        unzip = args.unzip
        jdcmd = args.jdcmd
        procyon = args.procyon
        apktool = args.apktool

    apk = args.apk_file
    basename = os.path.basename(apk)
    logger.debug('Target apk file is \'{}\''.format(basename))
    name, ext = os.path.splitext(basename)
    outdir = os.path.join(args.outdir, name)
    logger.debug('Output directory is \'{}\''.format(args.outdir))

    if (os.path.exists(tmp_dir)):
        logger.debug('Remove directory \'{}\''.format(tmp_dir))
        shutil.rmtree(tmp_dir)

    # Decompile
    if (jdcmd or procyon or unzip):

        logger.debug('Create directory \'{}\''.format(tmp_dir))
        os.makedirs(tmp_dir, exist_ok=True)

        # Unzip
        logger.info('--- Unzip apk file ---')
        logger.debug('Unzip \'{}\' to \'{}\''.format(apk, tmp_dir))
        with zipfile.ZipFile(apk) as existing_zip:
            dexFiles = [
                    file for file in existing_zip.namelist() if '.dex' in file]
            jarFiles = [file.replace('dex', 'jar') for file in dexFiles]
            existing_zip.extractall(tmp_dir)

        if (unzip):
            logger.debug('Copy \'{}\' to \'{}_unzip\''.format(tmp_dir, outdir))
            shutil.copytree(tmp_dir, outdir + '_unzip')

        # Dex to Jar
        if (jdcmd or procyon):
            logger.info('--- Convert Dex to Jar ---')
            for i, dex in enumerate(dexFiles):
                modules.function.call_subprocess(
                        [os.path.join(lib_path, 'dex-tools/d2j-dex2jar.sh'),
                            os.path.join(tmp_dir, dex), '-o',
                            os.path.join(tmp_dir, jarFiles[i])], level)

            # JavaDecompiler
            if (jdcmd):
                logger.info('--- Decompile using JavaDecompiler ---')
                for jar in jarFiles:
                    modules.function.call_subprocess(
                            [os.path.join(lib_path, 'jd-cmd/jd-cli'),
                                '-od', outdir + '_jdcmd',
                                os.path.join(tmp_dir, jar)], level)

            # Procyon Decompiler
            if (procyon):
                logger.info('--- Decompile using Procyon Decompiler ---')
                for jar in jarFiles:
                    modules.function.call_subprocess(
                            ['java', '-jar',
                                os.path.join(lib_path, 'procyon/procyon.jar'),
                                '-jar', os.path.join(tmp_dir, jar),
                                '-o', outdir + '_procyon'], level)

        logger.debug('--- Clean up ---')
        logger.debug('Remove directory \'{}\''.format(tmp_dir))
        shutil.rmtree(tmp_dir)

    # Decode
    if (apktool):
        logger.info('--- Decode using Apktool ---')
        modules.function.call_subprocess(
                ['apktool', 'decode', apk, '-o', outdir + '_apktool'], level)

    logger.info('Successfully')
