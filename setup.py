from setuptools import setup

setup(
    name = 'awstestutils',
    packages = ['awstestutils'],
    version = '0.1.0',
    description = 'Artifacts to test dependencies with AWS using boto3',
    long_description=open('README.rst').read(),

    install_requires = ['boto3'],

    test_suite='tests',

    author = 'Elvio Toccalino',
    author_email = 'me@etoccalino.com',
)
