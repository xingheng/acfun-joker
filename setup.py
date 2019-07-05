from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='acfun',
    version='0.2',
    author='Will Han',
    author_email='xingheng.hax@qq.com',
    license='MIT',
    keywords='acfun preview download',
    url='https://github.com/xingheng/acfun-joker',
    description='acfun video player',
    # long_description=long_description,
    # long_description_content_type='text/markdown',
    packages=['acfun'],
    include_package_data=True,
    install_requires=[
        'requests>=2.21.0',
        'lxml>=4.3.0',
        'click>=6.7'
    ],
    entry_points='''
        [console_scripts]
        acfun=acfun.acfun:cli
    ''',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Unix Shell',
        'Topic :: System :: Shells',
        'Topic :: Terminals',
        'Topic :: Text Processing :: Linguistic',
      ],
)
