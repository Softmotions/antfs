import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="antfs",
    version="1.0.2",
    author="Anton Adamansky",
    author_email="adamansky@gmail.com",
    description="Python3 Apache Ant path patterns matching library",
    license="MIT",
    keywords=["ant", "pattern", "matching", "glob", "regexp", "file", "selector"],
    url="https://github.com/Softmotions/antfs",
    packages=["antfs", "tests"],
    test_suite="tests",
    long_description=read("README.rst"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries",
        "Topic :: Utilities"
    ]
)