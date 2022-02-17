"""
    celery-sqlalchemy-scheduler
    ~~~~~~~~~~~~~~
    A Scheduler Based SQLalchemy For Celery.
    :Copyright (c) 2018 AngelLiang
    :license: MIT, see LICENSE for more details.
"""
from codecs import open
from os import path

try:
    from setuptools import find_packages, setup
except ImportError:
    from distutils.core import find_packages, setup  # type: ignore
# To use a consistent encoding

basedir = path.abspath(path.dirname(__file__))
# Get the long description from the README file
with open(path.join(basedir, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="celery_sqlalchemy_scheduler",
    python_requires=">=3.8",
    author="Aruba UXI",
    version="0.0.1",
    description="A Scheduler Based SQLalchemy For Celery",
    url="https://github.com/aruba-uxi/celery-sqlalchemy-scheduler",
    packages=find_packages(exclude=["contrib", "docs", "tests"]),
    include_package_data=True,
    zip_safe=False,
    install_requires=["celery>=4.2", "sqlalchemy"],
)
