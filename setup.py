from setuptools import setup

setup(
    name="tvdoon",
    version="1.3.0",
    author="LinArcX",
    author_email="linarcx@gmail.com",
    description="Display the ARM CPU and GPU temperature of Raspberry Pi",
    license=" GPL",
    keywords="PI, Raspberry, CPU , ARM, GPU",
    url="https://github.com/LinArcX/tvdoon",
    download_url='https://github.com/gavinlyonsrepo/raspeberrypi_tempmon/archive/1.4.tar.gz',
    packages=['rpiTempSrc','rpiTempMod',],
    install_requires= ['matplotlib','pip'],
    setup_requires = ['pip'],
    scripts=['rpiTempSrc/rpi_tempmon.py],
    classifiers=[
        "Development Status :: 3 - RTM",
        "Topic :: Utilities",
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
)