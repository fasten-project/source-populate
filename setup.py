from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='fastensource',
    version='0.0.1',
    description='A tool to download sources for FASTEN project',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='',
    author='',
    author_email='',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='',
    packages=find_packages(),
    python_requires='>=3.4, <4',
    install_requires=['lxml', 'requests', 'pydot', 'psycopg2-binary'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    # If there are data files included in your packages that need to be
    # installed, specify them here.
    #
    # If using Python 2.6 or earlier, then these have to be included in
    # MANIFEST.in as well.
    package_data={
        'fastensource': ['data/*.dat'],
    },

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files
    #
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    #  data_files=[('my_data', ['data/data_file'])],  # Optional

    entry_points={
        'console_scripts': [
            'fastensource=fastensource.__main__:main',
        ],
    },

    project_urls={  # Optional
        'Bug Reports': '',
        'Source': '',
    },
)
