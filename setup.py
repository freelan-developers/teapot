from setuptools import setup

setup(
    name='3party',
    version='1.0',
    long_description=__doc__,
    packages=[
        'three_party',
        'three_party.tests',
    ],
    install_requires=[
        'PyYaml',
    ],
    entry_points = {
        'console_scripts': [
            'tp = three_party.main:main',
        ],
    },
    test_suite='three_party.tests',
)
