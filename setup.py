# -*- coding: utf-8 -*-

# Learn more: https://github.com/kennethreitz/setup.py

from setuptools import setup, find_packages


with open("README.md") as f:
    readme = f.read()

setup(
    name="jobserver",
    version="0.0.1",
    description="A simple server to manage execution and artifacts of jobs.",
    long_description=readme,
    author="wh1ter0se",
    author_email="camelCaseEverything@gmail.com",
    url="https://github.com/wh1ter0se/job-server",
    # license=license,
    packages=find_packages(exclude=("tests", "docs")),
)
