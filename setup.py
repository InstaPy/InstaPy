# -*- coding: utf-8 -*-

from setuptools import find_packages
from setuptools import setup


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='instapy',
    version='0.1.0',
    description='Instagram Like/Comment/Follow Automation',
    long_description=readme,
    author='Tim Großmann',
    author_email='contact.timgrossmann@gmail.com',
    url='https://github.com/timgrossmann/InstaPy',
    license=license,
    packages=find_packages(exclude=('examples', 'assets'))
)
