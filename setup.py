from setuptools import setup

setup(
    name = 'awstestutils',
    packages = ['awstestutils'],
    version = '1.0.0',
    description = 'Artifacts to test dependencies with AWS using boto3',
    license = 'BSD',

    url = 'https://github.com/etoccalino/aws-test-utils',
    download_url = 'https://github.com/etoccalino/aws-test-utils/archive/v0.1.6.zip',
    keywords = ['aws', 'boto3', 'testing', 'tool'],
    long_description=open('README.rst').read(),

    install_requires = ['boto3'],
    test_suite='tests',

    author = 'Elvio Toccalino',
    author_email = 'me@etoccalino.com',

    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Testing',
        'Topic :: Utilities',
    ]
)
