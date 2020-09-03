from setuptools import setup, find_packages

setup(
    name='scrapy_promise',
    description='Promise-style workflow for Scrapy',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/monotony113/scrapy-promise',
    author='Tony Wu',
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
        'notcallback>=0.0.3',
    ],
)
