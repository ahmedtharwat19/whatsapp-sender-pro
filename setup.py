# setup.py
"""
ملف إعداد وتوزيع التطبيق
"""

from setuptools import setup, find_packages
import os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="whatsapp-sender-pro",
    version="1.0.0",
    author="Your Company",
    author_email="support@yourcompany.com",
    description="Professional WhatsApp Message Sending Software",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourcompany/whatsapp-sender-pro",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "whatsapp-sender=main:main",
        ],
    },
    package_data={
        "app": ["assets/*.png", "assets/*.ico"],
        "config": ["*.json", "*.yaml"],
    },
    data_files=[
        ("config", ["config/app_config.yaml"]),
    ],
    include_package_data=True,
    zip_safe=False,
)