from setuptools import setup, find_packages

setup(
    name="whatsapp_sender_pro",
    version="4.4.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "PyQt6>=6.5.0",
        "selenium>=4.15.0",
        "webdriver-manager>=4.0.1",
        "pandas>=2.1.0",
    ],
    extras_require={
        "full": [
            "Pillow>=10.1.0",
            "cryptography>=41.0.0",
            "requests>=2.31.0",
            "pyperclip>=1.8.2",
            "psutil>=5.9.0",
            "arabic-reshaper>=3.0.0",
            "python-bidi>=0.4.2",
            "deep-translator>=1.11.0",
            "openpyxl>=3.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "whatsapp-sender-pro=src.main:main",
        ],
    },
)