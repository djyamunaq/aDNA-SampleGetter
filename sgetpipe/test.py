import os
import sys
import subprocess

env = os.environ.copy()
env['PATH'] = env['PATH'] + ':' + os.path.abspath('./sratoolkit.3.0.10-ubuntu64/bin/')
# print(env['PATH'])
# print(os.path.abspath('./sratoolkit.3.0.10-ubuntu64/bin/'))
# subprocess.run(['parallel-fastq-dump', '--sra-id', 'ERR2206963', '--threads', '4','--split-files', '--gzip'])
subprocess.run(['parallel-fastq-dump', '--sra-id', 'ERR2206963', '--threads', '4','--split-files', '--gzip'], env=env)