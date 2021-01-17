import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="jonitan-chat",
    version="0.2.0",
    author="Yonatan Naisteter",
    author_email="skiba8150@gmail.com",
    description="Simple calculator implementation.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Jonitan/chat",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)