"""
Setup file for the dot2mmd package.
Run `pip install .` to install.
Run `pip install -e .` to install in editable mode for development.
"""

from setuptools import setup, find_packages

setup(
    name="dot2mmd",
    version="0.1.0",
    packages=find_packages(include=['dot2mmd', 'dot2mmd.*']),
    author="TripleJ Jacek",
    author_email="jjonca@gmail.com",
    description="A utility to convert Graphviz DOT files to MermaidJS syntax.",
    long_description="A utility to convert Graphviz DOT files to MermaidJS syntax.",
    long_description_content_type="text/markdown",
    url="https://github.com/jacek-jonca/dot2mmd",
    
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

