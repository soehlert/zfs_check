from setuptools import setup
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="zfs_check",
    version="0.6.0",
    description="Check on the health of your ZFS pools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # This should be a valid link to your project's main homepage.
    #
    # This field corresponds to the "Home-Page" metadata field:
    # https://packaging.python.org/specifications/core-metadata/#home-page-optional
    # url='https://github.com/pypa/sampleproject',  # Optional
    author="Sam Oehlert",
    author_email="sam.oehlert@gmail.com",
    classifiers=[  # Optional
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: System :: Filesystems",
        "Topic :: System :: Monitoring",
    ],
    keywords="zfs health monitor",
    py_modules=["zfs_check"],
    entry_points={"console_scripts": ["zfs_check=sample:main"]},
)
