# This Python file uses the following encoding: utf-8

from setuptools import setup
from os import path

# io.open is needed for projects that support Python 2.7
# It ensures open() defaults to text mode with universal newlines,
# and accepts an argument to specify the text encoding
# Python 3 only projects can skip this import and use built-in open()
from io import open as io_open
import re


summary = "Tool for automated Instagram interactions"
project_homepage = "https://github.com/timgrossmann/InstaPy"
here = path.abspath(path.dirname(__file__))


def readall(*args):
    with io_open(path.join(here, *args), encoding="utf-8") as fp:
        return fp.read()


with open("requirements.txt") as f:
    dependencies = f.read().splitlines()

documentation = readall("README.md")
metadata = dict(
    re.findall(r"""__([a-z]+)__ = "([^"]+)""", readall("instapy", "__init__.py"))
)

setup(
    name="instapy",
    version=metadata["version"],
    description=summary,
    long_description=documentation,
    long_description_content_type="text/markdown",
    author="Tim Großmann",
    author_email="contact.timgrossmann@gmail.com",
    maintainer="InstaPy Community at Github",
    license="GPLv3",
    url=project_homepage,
    download_url=(project_homepage + "/archive/master.zip"),
    project_urls={
        "How Tos": (project_homepage + "/tree/master/docs"),
        "Examples": (project_homepage + "/tree/master/quickstart_templates"),
        "Bug Reports": (project_homepage + "/issues"),
        "Funding": "https://www.paypal.me/supportInstaPy",
        "Say Thanks!": "http://saythanks.io/to/uluQulu",
        "Source": (project_homepage + "/tree/master/instapy"),
    },
    packages=["instapy"],
    # include_package_data=True,  # <- packs every data file in the package
    package_data={  # we need only the files below:
        "instapy": [
            "icons/Windows/*.ico",
            "icons/Linux/*.png",
            "icons/Mac/*.icns",
            "firefox_extension/*",
            "plugins/*",
        ]
    },
    keywords=(
        "instapy python instagram automation \
         marketing promotion bot selenium"
    ),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Environment :: Win32 (MS Windows)",
        "Environment :: MacOS X",
        "Environment :: Web Environment",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Unix",
        "Programming Language :: Python",
        "Programming Language :: JavaScript",
        "Programming Language :: SQL",
        "Topic :: Utilities",
        "Topic :: Software Development :: Build Tools",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Natural Language :: English",
    ],
    install_requires=dependencies,
    extras_require={"test": ["tox", "virtualenv", "tox-venv"]},
    python_requires=">=3, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
    platforms=["win32", "linux", "linux2", "darwin"],
    zip_safe=False,
    entry_points={"console_scripts": []},
)
