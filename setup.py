from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="chartpredictor",
    version="0.1.0",
    author="ChartPredictor Team",
    author_email="info@chartpredictor.com",
    description="Desktop application for trading chart analysis and prediction",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xplizet/ChartPredictor",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": ["pytest", "black", "flake8", "mypy"],
    },
    entry_points={
        "console_scripts": [
            "chartpredictor=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.ui", "*.qrc", "*.png", "*.jpg", "*.ico"],
    },
)