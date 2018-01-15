from setuptools import setup

setup(
    name='NMCT-Box',
    version='0.3.9',
    packages=['nmct', 'nmct.drivers', 'nmct.apis'],
    url='http://www.nmct.be',
    license='',
    author='Howest NMCT',
    author_email='',
    description='',
    install_requires=[
        'aiy', 'RPi.GPIO', 'snowboy', 'watson-developer-cloud', 'autobahn', 'Flask', 'smbus-cffi',
        'rpi-ws281x', 'spidev', 'matplotlib'
    ],
    data_files=[
        "../resources/snowboy/common.res"
        #     ('share/doc/aiy', ['README.md']),
        #     ('share/doc/aiy/examples', [
        #         "examples/vision/buzzer/congratulations.track",
        #         "examples/vision/buzzer/dramatic.track",
        #         "examples/vision/buzzer/laughing.track",
        #         "examples/vision/buzzer/sadtrombone.track",
        #         "examples/vision/buzzer/tetris.track",
        #     ])
    ],
    long_description=open('../README.md').read(),
    scripts=[
        "examples/watson_conversation.py",
        "examples/watson_translate.py",
        "examples/hotwords.py",
        "examples/sensors.py",
        "examples/pixelring.py",

    ]

)
