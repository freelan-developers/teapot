from setuptools import setup

import sys

install_requires = [
    'PyYaml',
    'requests>=1.2.3',
    'progressbar',
    'colorama',
    'LEPL',
]

if sys.version_info < (2, 7):
    install_requires.append('unittest2')

setup(
    name='tea-party',
    version='1.0',
    long_description=__doc__,
    packages=[
        'tea_party',
        'tea_party.environments',
        'tea_party.extensions',
        'tea_party.fetchers',
        'tea_party.unpackers',
        'tea_party.builders',
        'tea_party.filters',
        'tea_party.defaults',
        'tea_party.tests',
    ],
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'teapot = tea_party.main:main',
        ],
    },
    test_suite='tea_party.tests',
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Software Development',
        'License :: OSI Approved :: MIT License',
    ],
)
