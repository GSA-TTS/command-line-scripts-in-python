from setuptools import setup

setup(
    name='library admin tools',
    version='0.1.0',
    py_modules=['libadmin', 'pdf', 'lgr', 'util'],
    install_requires=[
        'click',
        'jinja2',
        'pandas',
        'pdfkit',
        'pytest',
        'requests',
        'xkcdpass'
    ],
    entry_points={
        'console_scripts': [
            'libadmin = libadmin:cli'
        ],
    },
)
