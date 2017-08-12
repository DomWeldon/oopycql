"""
OOPyCQL
-------------

An object oritneted interface for the Cypher Query Language in Python.
"""
try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

__author__ = 'Dom Weldon <dom.weldon@gmail.com>'
__email__ = 'dom.weldon@gmail.com'
__license__ = 'Apache License, Version 2.0'
__package__ = 'oopycql'
__version__ = '1.1.0a0'

setup(
    name='oopycql',
    version=__version__,
    url='https://github.com/DomWeldon/oopycql',
    license='Apache License, Version 2.0',
    author='Dom Weldon',
    author_email='dom.weldon@gmail.com',
    description='An object oritneted interface for the cypher query language',
    long_description=__doc__,
    packages=['oopycql'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'six',
        'regex',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Database",
    ],
    keywords='graph database neo4j cypher cql',
    test_suite='py.test',
    tests_require=['pytest'],
    setup_requires=['pytest-runner'],
    python_requires='>=2.7'#,
    #download_url='https://github.com/domweldon/flask_ogm/archive/1.1.0.tar.gz'
)
