from setuptools import setup, find_packages
import os

NAME = 'omayabias'
VERSION = '0.1.dev'
#datafiles = [(d, [os.path.join(d,f) for f in files])
#             for d, folders, files in os.walk('ogp_data')]

setup(
    name=NAME,
    version=VERSION,
    description='Python tools for 1mm OMAyA Receiver Bias',
    author='Gopal Narayanan <gopal@astro.umass.edu>',
    packages=find_packages(),
    scripts=['bin/omayasweep',],
    include_package_data=True,
    package_data = {
        '' : ['*.ui', '*.txt'],
        }
    #data_files=datafiles
)
