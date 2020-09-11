import os
import shutil
from setuptools import setup, find_packages


def clean_up(root='.'):
    try:
        shutil.rmtree(root + '/build')
    except FileNotFoundError:
        pass
    try:
        shutil.rmtree(root + '/dist')
    except FileNotFoundError:
        pass
    try:
        for f in os.listdir(root):
            if f[-9:] == '.egg-info':
                shutil.rmtree(root + '/' + f)
    except FileNotFoundError:
        pass


clean_up()


setup(
    name='scrapy_promise',
    description='Promise-style workflow for Scrapy',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/monotony113/scrapy-promise',
    author='Tony Wu',
    author_email='tony(dot)wu(at)nyu(dot)edu@inval.id',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries',
        'Framework :: Scrapy',
    ],
    packages=find_packages(),
    keywords='promise scrapy',
    python_requires='>=3.6',
    install_requires=[
        'notcallback>=0.0.8',
    ],
)
