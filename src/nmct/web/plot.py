import yaml
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
from bokeh.server.server import Server
from bokeh.themes import Theme
from bokeh.io import show, output_notebook

from nmct.box import get_accelerometer

# doc = curdoc()

theme = Theme(json=yaml.load("""
    attrs:
        Figure:
            background_fill_color: "#DDDDDD"
            outline_line_color: white
            toolbar_location: above
            height: 500
            width: 800
        Grid:
            grid_line_dash: [6, 4]
            grid_line_color: white
"""))


def plot_tilt(doc):
    p = figure(x_range=(-180, 180), y_range=(-180, 180))
    p.circle(x=0, y=0, radius=1, fill_color=None, line_width=2)

    # this is the data source we will stream to
    source = ColumnDataSource(data=dict(x=[1], y=[0]))
    p.circle(x='x', y='y', size=12, color='orange', fill_color='orange', source=source)

    am = get_accelerometer()

    def update():
        acc = am.tilt()
        source.stream(dict(x=[acc.roll], y=[acc.pitch]), rollover=8)

    doc.add_periodic_callback(update, 150)
    doc.add_root(p)
    doc.theme = theme


if __name__ == '__main__':
    server = Server({'/': plot_tilt}, num_procs=4)
    server.start()

    print('Opening Bokeh application on http://localhost:5006/')

    server.io_loop.add_callback(server.show, "/")
    server.io_loop.start()
