from setuptools import setup, find_packages

# ---------------------------------------------------------------------------
# Automatically discover all Python packages under src/
# ---------------------------------------------------------------------------
setup(
    name="ChickenDiseaseClassifier",
    version="0.0.1",
    author="Muhammad Basharat Asghar",
    author_email="mbasharatasghar1144@gmail.com",
    description="End-to-end CNN-based chicken disease classification system with MLOps",
    long_description=open("README.md").read() if __import__("os").path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    url="https://github.com/Basharat-Asghar/ChickenDieseaseClassification",
    package_dir={"": "src"},       # Root for package discovery is src/
    packages=find_packages(where="src"),
    python_requires=">=3.9",
    install_requires=[],           # Kept empty — dependencies live in requirements.txt
                                   # WHY: setup.py is for package metadata,
                                   # requirements.txt is for environment reproducibility.
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)