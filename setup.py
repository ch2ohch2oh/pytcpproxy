from setuptools import find_packages, setup

setup(
    name="pytcpproxy",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests",
    ],
    entry_points={
        "console_scripts": [
            "pytcpproxy = pytcpproxy.tcp_proxy:main",
        ],
    },
)
