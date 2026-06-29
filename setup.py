from setuptools import setup, find_packages
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="cbpi4-MCP23017-GPIO",
    version="0.0.3",
    description="CraftBeerPi4 MCP23017 GPIO Actor Plugin",
    author="gerrywin",
    author_email="gerrywin@users.noreply.github.com",
    url="https://github.com/gerrywin/cbpi4-MCP23017-GPIO",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["smbus2", "cbpi4>=4.1.10.rc2"],
    keywords="craftbeerpi4 cbpi4 i2c mcp23017 gpio actor brewing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
)
