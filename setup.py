"""
Setup file for the dot2mmd package.
Run `pip install .` to install.
Run `pip install -e .` to install in editable mode for development.
"""

from setuptools import setup
import pathlib

# Get the directory where setup.py is located
HERE = pathlib.Path(__file__).parent

# Read the contents of README.md using the full path
# Use .read_text() for automatic encoding handling
README = (HERE / "README.md").read_text()

setup(
    name="dot2mmd",
    version="0.1.0",
    packages=["dot2mmd"],
    author="TripleJ",
    author_email="jjonca@gmail.com",
    description="A utility to convert Graphviz DOT files to MermaidJS syntax.",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/jacek-jonca/dot2mmd", # Replace with your repo
    
    install_requires=[
        "pyparsing>=3.0.0",
    ],
    
    entry_points={
        "console_scripts": [
            "dot2mmd=dot2mmd.cli:main",
        ],
    },
    
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Compilers",
        "Topic :: Text Processing :: Markup",
    ],
    python_requires='>=3.7',
)

