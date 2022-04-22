"""
    :license: MIT, see LICENSE for more details.
"""

from setuptools import find_packages, setup

setup(
    name="uxi-celery-scheduler",
    python_requires=">=3.8",
    author="Aruba UXI",
    version="1.3.0",
    description="A SQLalchemy-based Scheduler For Celery Beat",
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
    install_requires=["celery~=5.2.3", "sqlalchemy", "alembic", "pydantic"],
)
