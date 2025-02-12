from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="system-monitor-cli",
    version="0.1.1",
    author="Inioluwa Adeyinka",
    author_email="boluwatifeeri@gmail.com",
    description="A comprehensive system monitoring tool with real-time insights",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/johnniewhite/watchtower",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: System :: Monitoring",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "rich>=13.0.0",
        "psutil>=5.9.0",
        "speedtest-cli>=2.1.3",
        "pynput>=1.7.0",
    ],
    entry_points={
        "console_scripts": [
            "system-monitor-cli=system_monitor:main",
        ],
    },
) 