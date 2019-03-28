"""
Install Somfy MyLink Synergy API
"""

from setuptools import setup, find_packages

with open('README.md') as f:
    LONG_DESCRIPTION = f.read()

setup(
    name='somfy_mylink_synergy',
    version='1.0.4',
    url='http://github.com/bendews/somfy-mylink-synergy',
    license='MIT',
    author='Ben Dews',
    author_email='contact@bendews.com',
    description='Python API to utilise the Somfy Synergy JsonRPC API',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    keywords='somfy mylink synergy covers sensors api jsonrpc',
    platforms='any'
)
