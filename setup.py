from setuptools import setup, find_packages

setup(
    name='initiative',
    version='0.1',
    description='Encounter creator/manager for DnD 5e',
    author='Nic Johnson',
    liscense='MIT',
    packages=find_packages(),
    zip_safe=False,
    install_requires=[
        'npyscreen',
        'cached-property',
        'prettytable',
    ],
    package_data={
        'initiative': [
            'monsters/*.json',
            'spells/*.json',
        ]
    },
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'initiative = initiative.main:main'
        ]
    }
)
