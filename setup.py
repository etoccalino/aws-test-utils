from distutils.core import setup

setup(
    name = "awstestutils",
    packages = ["awstestutils"],
    version = "0.1.0",
    description = "Artifacts to test dependencies with AWS using boto3",
    long_description=open('README.txt').read(),

    install_require = ['boto3'],

    author = "Elvio Toccalino",
    author_email = "me@etoccalino.com",
)
