from setuptools import setup, find_packages

setup(
    name='auto_model_monitor',
    version='0.1.2',
    description='A tool for monitoring model checkpoints and sending notifications',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='knighthood2001',
    author_email='2109695291@qq.com',
    url='https://github.com/Knighthood2001/model_monitor',
    packages=find_packages(),
    install_requires=[
        'yagmail'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
