from setuptools import setup
import geo2d

setup(
    name='Geo2D',
    version=geo2d.__version__,
    author='Razvan C. Radulescu',
    author_email='razvanc87@gmail.com',
    packages=['geo2d', 'geo2d.test'],
    scripts=[],
    url='http://launchpad.net/geo2d',
    license='LICENSE.txt',
    description='Pure Python (3 compatible) geometry package.',
    long_description=open('README.txt').read(),
    install_requires=[],
)
