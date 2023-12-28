from setuptools import setup

setup(
    name="rpi_tempmon.py",
    version="2.4",
    author="gavin lyons",
    author_email="glyons66@hotmail.com",
    description="Monitor RAM,CPU and GPU data  of Raspberry Pi",
    license=" GPL",
    keywords="PI Raspberry CPU ARM GPU temperature temp rpi monitor display gavin lyons",
    url="https://github.com/gavinlyonsrepo/raspeberrypi_tempmon",
    download_url='https://github.com/gavinlyonsrepo/raspeberrypi_tempmon/archive/2.4.tar.gz',
    packages=['rpiTempSrc','rpiTempMod',],
    install_requires= ['matplotlib','pip','psutil','RPi.GPIO'],
    setup_requires = ['pip'],
    scripts=['rpiTempSrc/rpi_tempmon.py'],
    classifiers=[
        "Topic :: Utilities",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
)
