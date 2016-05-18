from setuptools import setup, find_packages

import autorefresh

version = autorefresh.__version__

setup(
    name='autorefresh',
    description='Enabling app for browser autorefresh when django source changes',
    long_description="",
    version=version,
    author='Hari Mahadevan',
    author_email='hari@hari.xyz',
    url='https://www.github.com/harikvpy/django-autorefresh/',
    packages=[
        'autorefresh',
        ],
    include_package_data=True,
    install_requires=[],
    license='BSD-3',
    keywords=[
        'django',
        'autorefresh',
        'autoreload',
        ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        ],
    )
