from setuptools import setup

setup(
    name='NMCT-Box',
    version='0.3.21',
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
        'aiy', 'RPi.GPIO', 'snowboy', 'watson-developer-cloud', 'autobahn', 'Flask', 'smbus-cffi',
        'rpi-ws281x', 'spidev', 'matplotlib', 'uwsgi', 'jupyter', 'jupyterthemes', 'jupyterhub', 'bokeh',
        'pandas', 'widgetsnbextension'
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
    long_description=open('../README.md').read(),
    scripts=[
        "examples/watson_conversation.py",
        "examples/watson_translate.py",
        "examples/nmct_box_demo.py",
        "examples/hotwords.py",
        "examples/sensors.py",
        "examples/pixelring.py",
    ]
)
