from setuptools import setup, find_packages

setup(
    name='universal',
    version='0.1.0',  # update the version number as appropriate
    description='A collection of utilities for remote SSH connections and configuration file management',
    author='Your Name',
    author_email='your.email@example.com',
    url='http://github.com/jsailsbery/universal',
    packages=find_packages(),
    install_requires=[
        'paramiko>=2.7.2',  # add other dependencies as needed
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',  # update as appropriate
        'Programming Language :: Python :: 3.8',  # update as appropriate
        'Programming Language :: Python :: 3.9',  # update as appropriate
        'Programming Language :: Python :: 3.10'  # update as appropriate
    ],
)
