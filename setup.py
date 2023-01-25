from setuptools import setup

setup(
    name='admin tools',
    version='0.1.0',
    py_modules=['check'],
    install_requires=[
        'click',
        'pandas',
        'peewee'
    ],
    entry_points={
        'console_scripts': [
            'check = check:cli',
        ],
    },
)
