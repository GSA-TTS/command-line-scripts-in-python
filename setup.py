from setuptools import setup

setup(
    name='library admin tools',
    version='0.1.0',
    py_modules=['check', 'extend', 'upload'],
    install_requires=[
        'click',
        'pandas',
        'peewee',
        'pytest',
        'requests',
        'xkcdpass'
    ],
    entry_points={
        'console_scripts': [
            'check = check:cli',
            'extend = extend:cli',
            'upload = upload:cli'
        ],
    },
)
