from setuptools import setup

setup(
    name='tea-party',
    version='1.0',
    long_description=__doc__,
    packages=[
        'tea_party',
        'tea_party.fetchers',
        'tea_party.tests',
    ],
    install_requires=[
        'PyYaml',
    ],
    entry_points={
        'console_scripts': [
            'tp = tea_party.main:main',
        ],
    },
    test_suite='tea_party.tests',
)
