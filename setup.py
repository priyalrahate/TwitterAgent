"""
Setup script for Twitter Agent
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="twitter-agent",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="AI-powered Twitter automation agent with Fetch.ai and ChatGPT integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/twitter-agent",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.21.1",
            "black>=23.11.0",
            "flake8>=6.1.0",
            "mypy>=1.7.1",
            "pre-commit>=3.5.0",
        ],
        "prod": [
            "gunicorn>=21.2.0",
            "uvicorn[standard]>=0.24.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "twitter-agent=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.json", "*.yaml", "*.yml", "*.md", "*.txt"],
    },
    keywords=[
        "twitter",
        "ai",
        "agent",
        "automation",
        "fetch-ai",
        "chatgpt",
        "openai",
        "social-media",
        "workflow",
        "scheduler",
    ],
    project_urls={
        "Bug Reports": "https://github.com/yourusername/twitter-agent/issues",
        "Source": "https://github.com/yourusername/twitter-agent",
        "Documentation": "https://github.com/yourusername/twitter-agent/wiki",
    },
)
