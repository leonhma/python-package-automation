# this file will never change its version. thats because a copy of this file is changed and afterwards deleted

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="<>",
    version="<>",
    author="<>",
    author_email="leonhard.masche@gmail.com",
    description="example package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/leonhma/lemon_markets",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent"
    ],
    install_requires=[
        'datetime',
        'time',
        'urllib3',
        'websocket',
        'multiprocessing'
    ]
)
