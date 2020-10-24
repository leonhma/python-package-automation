# this file contains some placeholders
# that are changed in a local copy if a release is made

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="<>",  # placeholder (name of repo)
    version="<>",  # placeholder (tag of release)
    author="<>",  # placeholder (owner of repo)
    author_email="none@none.com",
    description="<>",  # placeholder (description of repo)
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
        'urllib3',
        'websocket'
    ]
)
