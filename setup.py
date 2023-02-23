# encoding:utf-8
import setuptools

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='serial',
    version='0.0.1',
    author='sunlulu.tomato',
    author_email='sunlulu.tomato@bytedance.com',
    description='A simple python serialize and deserialize tools',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
