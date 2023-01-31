from setuptools import setup

setup(
    name='library admin tools',
    version='0.1.0',
    py_modules=['check', 'upload', 'libadmin'],
    install_requires=[
        'click',
        'jinja2',
        'pandas',
        'pdfkit',
        'peewee',
        'pytest',
        'requests',
        'xkcdpass'
    ],
    entry_points={
        'console_scripts': [
            'check = check:cli',
            'upload = upload:cli',
            'libadmin = libadmin:cli'
        ],
    },
)
