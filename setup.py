from setuptools import setup, find_packages

# TODO(nknight): include template files

install_requires = [
        "pypeg2 >= 2.15.2, <3",
        "pystache >=0.5.4, <0.6",
        "SQLAlchemy >=1.1.14, <2.0",
]

tests_require = [
    "pycodestyle >=2.3.1, <3.0",
    "flake8 >= 3.5.0, <4.0",
]


setup(
    name="shared_schema",
    version="0.1",
    author="Nathaniel Knight",
    author_email="nknight@cfenet.ubc.ca",
    url="https://github.com/hcv-shared/shared-schema",
    packages=find_packages(),
    install_requires=install_requires,
    extras_require={
        "tests": tests_require,
    },
    test_suite='test',
)
