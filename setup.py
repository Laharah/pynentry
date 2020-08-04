import pathlib
from setuptools import setup

HERE = pathlib.Path(__file__).parent

README = (HERE / 'README.md').read_text()

setup(
    name='pynentry',
    version='0.1.2',
    description='A pythonic wrapper around pinentry for secure password input',
    long_description=README,
    long_description_content_type="text/markdown",
    url='https://github.com/Laharah/pynentry',
    author='laharah',
    author_email='laharah22+pyn@gmail.com',
    license='MIT',
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: Security",
        "Topic :: Software Development :: User Interfaces",
    ],
    py_modules=['pynentry'],
)
