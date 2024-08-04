#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open("README.md") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()


test_requirements = []

setup(
    author="Ana Sofia Carmo",
    author_email="anascacais@gmail.com",
    python_requires=">=3.6, <3.10",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    description="EpiBOX is a Raspberry Pi tool for easy signal acquisition.",
    entry_points={
        "console_scripts": [
            "epibox=epibox.cli:main",
        ],
    },
    install_requires=[
        "bitalino==1.2.1",
        "numpy==1.21.0; sys_platform != 'win32'",
        "numpy; sys_platform == 'win32'",
        "pywin32; sys_platform == 'win32'",
        "paho-mqtt==1.5.1",
        "pyserial==3.5",
        "pybluez2; sys_platform != 'darwin'",
        "scientisst-sense==1.0.5",
        "scipy",
        "bump"
    ],
    license="MIT license",
    long_description_content_type="text/markdown",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords=["epibox", "signal acquisition", "Raspberry Pi"],
    name="epibox",
    packages=find_packages(include=["epibox", "epibox.*"]),
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/anascacais/epibox",
    version="3.0.0",
    zip_safe=False,
)
