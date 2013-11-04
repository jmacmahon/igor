"""Package metadata"""

from __future__ import unicode_literals

import setuptools

setuptools.setup(
    name = "igor",
    version = "0.2.0",
    url = "https://github.com/borntyping/igor",

    author = "Sam Clements",
    author_email = "sam@borntyping.co.uk",

    description = "An IRC bot reanimated from various other bots",
    long_description = open('README.md').read(),

    packages = setuptools.find_packages(),

    entry_points = {
        'console_scripts': [
            'igor = igor:main'
        ]
    },

    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'License :: OSI Approved',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Communications',
        'Topic :: Communications :: Chat',
        'Topic :: Communications :: Chat :: Internet Relay Chat',
    ],
)
