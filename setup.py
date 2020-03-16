import setuptools


setuptools.setup(
    name="validate-approvals",
    version="0.0.1",
    author="Drew Ayling",
    author_email="dsayling@gmail.com",
    description="provides an approval gate",
    url="https://github.com/dsayling/app-gate",
    packages=setuptools.find_packages(),
    scripts=['bin/validate_approvals',
    ],
    python_requires='>=3.6',
)