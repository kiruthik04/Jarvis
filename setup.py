from setuptools import setup, find_packages

setup(
    name="jarvis",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "huggingface_hub",
        "pyautogui",
        "beautifulsoup4",
        "selenium",
        "webdriver-manager",
        "python-dotenv",
        "requests",
    ],
)
