from bokeh.io import curdoc
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure

from nmct.hardware import get_accelerometer

p = figure(x_range=(-180, 180), y_range=(-180, 180))
p.circle(x=0, y=0, radius=1, fill_color=None, line_width=2)

# this is the data source we will stream to
source = ColumnDataSource(data=dict(x=[1], y=[0]))
p.circle(x='x', y='y', size=12, fill_color='white', source=source)

am = get_accelerometer()


def update():
    acc = am.tilt()
    source.stream(dict(x=[acc.roll], y=[acc.pitch]), rollover=8)


curdoc().add_periodic_callback(update, 150)
curdoc().add_root(p)

