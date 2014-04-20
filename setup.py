from setuptools import setup

import sys

install_requires = [
    'requests>=1.2.3',
    'progressbar',
    'colorama',
    'LEPL',
]

if sys.version_info < (2, 7):
    install_requires.append('unittest2')

setup(
    name='teapot',
    url='http://teapot-builder.readthedocs.org/en/latest/index.html',
    author='Julien Kauffmann',
    author_email='julien.kauffmann@freelan.org',
    license='MIT License',
    version=open('VERSION').read().strip(),
    description="A multi-platform tool to automate the download, unpack and build of third-party softwares.",
    long_description="""\
teapot is a python library and a command-line tool that eases the
downloading, the unpacking and the building of third-party softwares in a
project.

teapot comes with the command-line tool `teapot` that does all the
necessary work.

teapot is designed with extension in mind, which means it is very easy
to add your own modules and extend its scope.
""",
    packages=[
        'teapot',
        'teapot.filters',
        'teapot.fetchers',
        'teapot.unpackers',
        'teapot.extra',
    ],
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'teapot = teapot.main:main',
        ],
    },
    test_suite='teapot.tests',
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
