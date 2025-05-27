from setuptools import setup, find_packages

setup(
    name="DijurLib",
    version="0.0.13.4",
    packages=find_packages(),
    install_requires=[
        "selenium",
        "requests"
        ],
    description="Biblioteca interna da DIJUR",
    author="DIJUR",
)
