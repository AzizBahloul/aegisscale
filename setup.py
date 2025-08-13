from setuptools import setup, find_packages

# Automatically read requirements.txt
with open("requirements.txt") as f:
    required = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="aegisscale",
    version="1.0.0",
    description="A Kubernetes autoscaler using reinforcement learning",
    author="Aziz Bahloul",
    author_email="",
    url="https://github.com/AzizBahloul/aegisscale",
    packages=find_packages(exclude=["tests*", "deploy*", ".github"]),
    install_requires=required,
    entry_points={
        "console_scripts": [
            "aegisscale=aegisscale.main:cli",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
