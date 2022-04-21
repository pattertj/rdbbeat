"""
    :license: MIT, see LICENSE for more details.
"""

from setuptools import find_packages, setup

setup(
    name="uxi-celery-scheduler",
    python_requires=">=3.8",
    author="Aruba UXI",
    version="1.0.0",
    description="A Scheduler Based SQLalchemy For Celery",
    classifiers=[
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3",
    ],
    url="https://github.com/aruba-uxi/celery-sqlalchemy-scheduler",
    packages=find_packages(exclude=["contrib", "docs", "tests"]),
    include_package_data=True,
    zip_safe=False,
    install_requires=["celery>=4.2", "sqlalchemy"],
)
