import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="lemon_markets",
    version="0.0.1",
    author="leonhma",
    author_email="author@example.com",
    description="lemon_markets is an (inofficial) python wrapper for various lemon.market endpoints.'\
        ' This includes a WebSocket client based on callbacks and an easy way to acces account and intraday data.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/leonhma/lemon_markets",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Natural Language :: English"
    ],
    python_requires='>=3.6',
    install_requires=[
        'datetime',
        'time',
        'urllib3',
        'websocket',
        'multiprocessing'
    ]
)
