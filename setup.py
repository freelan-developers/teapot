from setuptools import setup

setup(
    name='tea-party',
    version='1.0',
    long_description=__doc__,
    packages=[
        'tea_party',
        'tea_party.fetchers',
        'tea_party.unpackers',
        'tea_party.builders',
        'tea_party.defaults',
        'tea_party.tests',
    ],
    install_requires=[
        'PyYaml',
        'requests>=1.2.3',
        'rfc6266',
        'progressbar',
    ],
    entry_points={
        'console_scripts': [
            'teapot = tea_party.main:main',
        ],
    },
    test_suite='tea_party.tests',
)
