from setuptools import setup

setup(
    name='3party',
    version='1.0',
    long_description=__doc__,
    packages=[
        'three_party',
    ],
    install_requires=[
        'Fabric',
    ],
    entry_points = {
        'console_scripts': [
            'tp = three_party.main:main',
        ],
    },
)
