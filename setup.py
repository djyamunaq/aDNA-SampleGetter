from setuptools import setup
setup(
    name = 'sampleGetter-pipeline',
    version = '0.1.0',
    packages = ['sgetpipe'],
    entry_points = {
        'console_scripts': [
            'sgetpipe = sgetpipe.__main__:main'
        ]
    })