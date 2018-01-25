from setuptools import setup

setup(
    name='NMCT-Box',
    version='1.0.0',
    description='NMCT Box framework',
    package_dir={'': 'src'},
    packages=['nmct', 'nmct.drivers', 'nmct.apis', 'nmct.web'],
    package_data={'nmct.web': ['static/*', 'templates/*']},
    url='http://www.nmct.be',
    license='',
    author='Howest NMCT',
    author_email='',
    maintainer='NMCT',
    maintainer_email='info@nmct.be',
    install_requires=[
        'aiy', 'snowboy', 'RPi.GPIO', 'watson-developer-cloud', 'autobahn', 'flask', 'smbus-cffi',
        'rpi-ws281x', 'spidev', 'matplotlib', 'uwsgi', 'bokeh', 'netifaces'
    ],
    data_files=[
        #     ('share/doc/aiy', ['README.md']),
        #     ('share/doc/aiy/examples', [
        #         "examples/vision/buzzer/congratulations.track",
        #         "examples/vision/buzzer/dramatic.track",
        #         "examples/vision/buzzer/laughing.track",
        #         "examples/vision/buzzer/sadtrombone.track",
        #         "examples/vision/buzzer/tetris.track",
        #     ])
    ],
    # TODO: audio files, see https://docs.python.org/3.6/distutils/setupscript.html#installing-package-data
    long_description=open('README.md').read(),
    scripts=[
        "src/examples/watson_conversation.py",
        "src/examples/watson_translate.py",
        "src/examples/nmct_box_demo.py",
        "src/examples/hotwords.py",
        "src/examples/sensors.py",
        "src/examples/pixelring.py",
    ]
)
# python3-autobahn python3-websockets python3-flask python3-matplotlib uwsgi python3-smbus python3-spidev
# python3-notebook python3-widgetsnbextension python3-nbformat python3-nbconvert python3-jupyter-console
# jupyter-nbformat jupyter-nbformat jupyter-nbextension-jupyter-js-widgets jupyter-nbconvert jupyter-core
# jupyter-client jupyter-console python3-pandas python3-netifaces python3-numpy

