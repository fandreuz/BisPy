import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="BisPy",
    version="0.1.0",

    author="Francesco Andreuzzi",
    author_email="andreuzzi.francesco@gmail.com",

    description="A bisimulation library for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",

    url="https://github.com/fAndreuzzi/BisPy",
    project_urls={
        "Bug Tracker": "https://github.com/fAndreuzzi/BisPy/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],

    package_dir={"": "bispy"},
    packages=setuptools.find_packages(where="bispy"),
    python_requires=">=3.5",
)
