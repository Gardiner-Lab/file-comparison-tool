#!/usr/bin/env python3
"""
Setup script for File Comparison Tool

This script handles the packaging and distribution of the File Comparison Tool.
It can create both source distributions and standalone executables.
"""

from setuptools import setup, find_packages
import os
import sys

# Read version and metadata from main.py
def get_version():
    """Extract version from main.py"""
    with open('main.py', 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('"')[1]
    return "1.0.0"

def get_long_description():
    """Read the README file for long description"""
    try:
        with open('README.md', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "A GUI application for comparing Excel and CSV files with various operations"

# Application metadata
VERSION = get_version()
DESCRIPTION = "A GUI application for comparing Excel and CSV files with various operations"
LONG_DESCRIPTION = get_long_description()
AUTHOR = "File Comparison Tool Team"
EMAIL = "support@filecomparisontool.com"
URL = "https://github.com/yourusername/file-comparison-tool"

# Requirements
INSTALL_REQUIRES = [
    'pandas>=1.5.0',
    'openpyxl>=3.0.0',
    'xlrd>=2.0.0',
]

EXTRAS_REQUIRE = {
    'dev': [
        'psutil>=5.9.0',
        'memory-profiler>=0.60.0',
        'pytest>=7.0.0',
        'pytest-cov>=4.0.0',
    ],
    'build': [
        'pyinstaller>=5.0.0',
        'auto-py-to-exe>=2.20.0',
    ]
}

# Entry points
ENTRY_POINTS = {
    'console_scripts': [
        'file-comparison-tool=main:main',
        'fct=main:main',
    ],
    'gui_scripts': [
        'file-comparison-tool-gui=main:main',
    ]
}

# Package data
PACKAGE_DATA = {
    '': ['*.md', '*.txt', '*.yml', '*.yaml'],
    'src': ['**/*.py'],
    'docs': ['*.md', '*.html'],
    'test_data': ['*.csv', '*.xlsx'],
}

# Classifiers
CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: End Users/Desktop',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11',
    'Topic :: Office/Business :: Financial :: Spreadsheet',
    'Topic :: Utilities',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Environment :: X11 Applications',
    'Environment :: Win32 (MS Windows)',
    'Environment :: MacOS X',
]

setup(
    name='file-comparison-tool',
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    package_data=PACKAGE_DATA,
    include_package_data=True,
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE,
    entry_points=ENTRY_POINTS,
    classifiers=CLASSIFIERS,
    python_requires='>=3.8',
    keywords='excel csv file comparison data processing gui',
    project_urls={
        'Bug Reports': f'{URL}/issues',
        'Source': URL,
        'Documentation': f'{URL}/wiki',
    },
    zip_safe=False,
)