import setuptools


with open("README.md") as fp:
    long_description = fp.read()


setuptools.setup(
    name="java_goof_ecs_construct",
    version="0.0.1",
    description="java_goof_ecs_construct",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="author",
    package_dir={"": "java_goof_ecs_construct"},
    packages=setuptools.find_packages(where="cdk"),
    install_requires=[
        "aws-cdk.core==1.83.0",
        "aws-cdk.aws_ec2==1.83.0",
        "aws-cdk.aws_ecs==1.83.0",
        "aws-cdk.aws_iam==1.83.0",
        "aws-cdk.aws_ecs_patterns==1.83.0",
        "aws-cdk.aws_logs==1.83.0",
        "aws-cdk.aws_ssm==1.83.0",
    ],
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",
        "Typing :: Typed",
    ],
)
