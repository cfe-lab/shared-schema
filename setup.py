from setuptools import find_packages, setup

# TODO(nknight): include template files

install_requires = [
    "pypeg2 >= 2.15.2, <3",
    "pystache >=0.5.4, <0.6",
    "SQLAlchemy >=1.1.14, <2.0",
]

tests_require = ["flake8 >= 3.5.0, <4.0"]

setup(
    name="shared_schema",
    version="0.1",
    author="Nathaniel Knight",
    author_email="nknight@cfenet.ubc.ca",
    url="https://github.com/hcv-shared/shared-schema",
    packages=find_packages(),
    package_dir={"shared_schema": "shared_schema"},
    package_data={"shared_schema": ["templates/*.mustache"]},
    python_requires="~= 3.5",
    install_requires=install_requires,
    extras_require={"tests": tests_require},
    test_suite="test",
)
