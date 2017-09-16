from setuptools import setup, find_packages

# TODO(nknight): include template tiles

setup(
    name="shared_schema",
    version="0.1",
    author="Nathaniel Knight",
    author_email="nknight@cfenet.ubc.ca",
    url="https://github.com/neganp/shared-schema",
    packages=find_packages(),
    install_requires=[
        "pypeg2 >= 2.15.2, <3",
        "pystache >=0.5.4, <0.6",
        "setuptools >=36.1.1, <37.0",
    ],
)
