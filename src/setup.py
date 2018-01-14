from setuptools import setup

setup(
    name='NMCT-Box',
    version='0.3.0',
    packages=['nmct', 'nmct.drivers', 'nmct.apis'],
    url='http://www.nmct.be',
    license='',
    author='Howest NMCT',
    author_email='',
    description='',
    install_requires=[
        'aiy', 'RPi.GPIO', 'snowboy', 'watson-developer-cloud', 'autobahn'
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
    # long_description=open('README.md').read(),
    scripts=[
        "examples/watson_demo.py",

    ]

)
