import os
from setuptools import find_packages, setup
from asgiref import __version__


# We use the README as the long_description
readme_path = os.path.join(os.path.dirname(__file__), "README.rst")


setup(
    name='asgiref',
    version=__version__,
    url='http://github.com/django/asgiref/',
    author='Django Software Foundation',
    author_email='foundation@djangoproject.com',
    description='ASGI specs, helper code, and adapters',
    long_description=open(readme_path).read(),
    license='BSD',
    zip_safe=False,
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    extras_require={
        "tests": [
            "pytest~=3.3",
            "pytest-asyncio~=0.8",
        ],
    },
    install_requires=[
        'async-timeout~=2.0',
    ],
)
