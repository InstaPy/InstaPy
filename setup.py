io
import os
from setuptools import setup




__version__ = '0.0.1'
__author__ = 'Tim Grossmann'

with open("requirements.txt") as f:
    dependencies = f.read().splitlines()

try:
    with io.open(os.path.join(here, "changelog.md"), encoding="utf-8") as cl_file:
        changes_made = '\n' + cl_file.read()
except FileNotFoundError:
    changes_made = ""

description = 'Instagram Like, Comment and Follow Automation Script'

here = os.path.abspath(os.path.dirname(__file__))
with io.open(os.path.join(here, "README.md"), encoding="utf-8") as doc_file:
    documentation = '\n' + doc_file.read()



setup(
    name='instagram_py',
    version=__version__,
    description=description,
    long_description=documentation,
    changelog=changes_made,
    author=__author__,
    author_email='contact.timgrossmann@gmail.com',
    maintainer="InstaPy Community at Github",
    url='https://github.com/timgrossmann/InstaPy',
    download_url="https://github.com/timgrossmann/InstaPy/archive/master.zip",
    project_urls={"GUI": "https://github.com/ahmadudin/electron-instaPy-GUI",
                  "How Tos": "https://github.com/timgrossmann/InstaPy/tree/master/docs",
                  "Examples": "https://github.com/timgrossmann/InstaPy/tree/master/examples"},
    packages=['instapy'],
    py_modules='instapy',
    license="GPLv3",
    keywords=["instagram", "automation", "promotion", "marketing", "instapy", "bot"],
    classifiers=["Development Status :: 5 - Production/Stable",
                 "Environment :: Console",
                 "Environment :: Win32 (MS Windows)",
                 "Environment :: MacOS X",
                 "Environment :: Web Environment",
                 "Environment :: Other Environment :: VPS",
                 "Intended Audience :: End Users/Desktop",
                 "Intended Audience :: Developers",
                 "License :: OSI Approved :: GNU General Public License v3",
                 "Operating System :: Microsoft :: Windows",
                 "Operating System :: POSIX :: Linux",
                 "Operating System :: MacOS :: MacOS X",
                 "Operating System :: Unix",
                 "Programming Language :: Python",
                 "Programming Language :: JavaScript",
                 "Programming Language :: SQL",
                 "Topic :: Internet :: Browsers",
                 "Topic :: Other/Nonlisted Topic :: Automation :: Selenium",
                 "Topic :: Utilities",
                 "Natural Language :: English"],
    install_requires=dependencies,
    extras_require={},
    tests_require=["pytest"],
    include_package_data=True,
    python_requires=">=2.7",
    platforms=["win32", "linux", "linux2", "darwin"]
    )



