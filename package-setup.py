from setuptools import setup, find_packages
import os

def read_requirements(filename):
    """Read requirements from a file."""
    with open(filename, 'r') as file:
        return [line.strip() for line in file 
                if line.strip() and not line.startswith('#')]

def read_long_description():
    """Read long description from README.md."""
    try:
        with open('README.md', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Claude Desktop Multi-Component Platform (MCP)"

setup(
    name='claude-desktop-mcp',
    version='0.1.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='Multi-Component Platform for AI-driven Productivity and Experimentation',
    long_description=read_long_description(),
    long_description_content_type='text/markdown',
    url='https://github.com/seanpoyner/claude-desktop-mcp-playground',
    packages=find_packages(exclude=['tests*', 'docs']),
    install_requires=read_requirements('requirements.txt'),
    extras_require={
        'dev': read_requirements('requirements.txt'),
        'gpu': [
            'cupy>=12.0.0',
            'torch-cuda>=2.1.0',
            'tensorflow-gpu>=2.13.0'
        ]
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.9',
    entry_points={
        'console_scripts': [
            'claude-desktop-mcp=claude_desktop_mcp.cli:main',
        ],
    },
    keywords='ai productivity workflow agent platform claude anthropic',
    project_urls={
        'Bug Reports': 'https://github.com/seanpoyner/claude-desktop-mcp-playground/issues',
        'Source': 'https://github.com/seanpoyner/claude-desktop-mcp-playground',
    },
)