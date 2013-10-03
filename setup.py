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
    url='http://tea-party.readthedocs.org/en/latest/index.html',
    author='Julien Kauffmann',
    author_email='julien.kauffmann@freelan.org',
    license='MIT License',
    version='1.0',
    description="A multi-platform tool to automate the download, unpack and build of third-party softwares.",
    long_description="""\
tea-party is a python library and a command-line tool that eases the
downloading, the unpacking and the building of third-party softwares in a
project.

tea-party comes with the command-line tool `teapot` that does all the
necessary work.

tea-party is designed with extension in mind, which means it is very easy
to add your own modules and extend its scope.
""",
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
        'tea_party.extra',
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
