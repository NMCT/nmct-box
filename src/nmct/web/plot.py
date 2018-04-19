import yaml
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, datetime, MultiLine, Label
from bokeh.plotting import figure
from bokeh.server.server import Server
from bokeh.themes import Theme
from bokeh.io import show, output_notebook

from nmct.box import get_accelerometer, measure_temperature

# doc = curdoc()

theme = Theme(json=yaml.load("""
    attrs:
        Figure:
            background_fill_color: "#303030"
            border_fill_color: "#424242"
            outline_line_color: white
            toolbar_location: above
            height: 500
            width: 800
        Axis:
            axis_line_color: "white"
            axis_label_text_color: "white"
            major_label_text_color: "white"
            major_tick_line_color: "white"
            minor_tick_line_color: "white"
            minor_tick_line_color: "white"
        Grid:
            grid_line_dash: [6, 4]
            grid_line_color: gray
            grid_line_alpha: .3
        Title:
            text_color: "white"
"""))
# JS_CODE = """
# import {Label, LabelView} from "models/annotations/label"
#
# export class LatexLabelView extends LabelView
#   render: () ->
#
#     #--- Start of copied section from ``Label.render`` implementation
#
#     # Here because AngleSpec does units tranform and label doesn't support specs
#     switch @model.angle_units
#       when "rad" then angle = -1 * @model.angle
#       when "deg" then angle = -1 * @model.angle * Math.PI/180.0
#
#     panel = @model.panel ? @plot_view.frame
#
#     xscale = @plot_view.frame.xscales[@model.x_range_name]
#     yscale = @plot_view.frame.yscales[@model.y_range_name]
#
#     sx = if @model.x_units == "data" then xscale.compute(@model.x) else panel.xview.compute(@model.x)
#     sy = if @model.y_units == "data" then yscale.compute(@model.y) else panel.yview.compute(@model.y)
#
#     sx += @model.x_offset
#     sy -= @model.y_offset
#
#     #--- End of copied section from ``Label.render`` implementation
#
#     # Must render as superpositioned div (not on canvas) so that KaTex
#     # css can properly style the text
#     @_css_text(@plot_view.canvas_view.ctx, "", sx, sy, angle)
#
#     # ``katex`` is loaded into the global window at runtime
#     # katex.renderToString returns a html ``span`` element
#     katex.render(@model.text, @el, {displayMode: true})
#
# export class LatexLabel extends Label
#   type: 'LatexLabel'
#   default_view: LatexLabelView
# """

#
# class LatexLabel(Label):
#     """A subclass of the Bokeh built-in `Label` that supports rendering
#     LaTex using the KaTex typesetting library.
#
#     Only the render method of LabelView is overloaded to perform the
#     text -> latex (via katex) conversion. Note: ``render_mode="canvas``
#     isn't supported and certain DOM manipulation happens in the Label
#     superclass implementation that requires explicitly setting
#     `render_mode='css'`).
#     """
#     __javascript__ = ["https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.6.0/katex.min.js"]
#     __css__ = ["https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.6.0/katex.min.css"]
#     __implementation__ = JS_CODE


def plot_temperature(document):
    starttime = datetime.now()
    plot = figure(x_axis_type="datetime", plot_width=800, tools="", toolbar_location=None, y_range=(-10, 40))

    # this is the data source we will stream to
    source = ColumnDataSource(data=dict(x=[(starttime - datetime.now()).seconds], y=[measure_temperature()]))
    plot.line(x='x', y='y', color='red', source=source, line_width=3)

    def update():
        t = measure_temperature()
        source.stream(dict(x=[(starttime - datetime.now()).seconds], y=[t]), rollover=300)

    plot.title.text = "Temperature"
    plot.yaxis.axis_label = 'Temperature (Celsius)'
    document.add_periodic_callback(update, 500)
    document.add_root(plot)
    document.theme = theme


def plot_tilt(document):
    plot = figure(x_range=(-180, 180), y_range=(-180, 180))
    plot.circle(x=0, y=0, radius=1, fill_color=None, line_width=2)

    # this is the data source we will stream to
    source = ColumnDataSource(data=dict(x=[1], y=[0]))
    plot.circle(x='x', y='y', size=12, color='orange', fill_color='orange', source=source)

    am = get_accelerometer()

    def update():
        tilt = am.tilt()
        source.stream(dict(x=[tilt.roll], y=[tilt.pitch]), rollover=8)

    plot.title.text = "Tilt"
    plot.xaxis.axis_label = "Roll"
    plot.yaxis.axis_label = "Pitch"
    document.add_periodic_callback(update, 150)
    document.add_root(plot)
    document.theme = theme


def plot_acceleration(document):
    starttime = datetime.now()
    plot = figure(x_axis_type="datetime", plot_width=800, tools="", toolbar_location=None,
                  y_range=(-20, 20))
    am = get_accelerometer()
    acc = am.measure()
    # this is the data source we will stream to
    # source = ColumnDataSource(data=dict(xs=[int((starttime - datetime.now()).seconds)] * 3,
    #                                     ys=[acc.x, acc.y, acc.z], line_color=['red', 'green', 'blue']))
    # glyph = MultiLine(xs='xs', ys='ys', line_color='line_color')  # , line_color='green'
    # plot.add_glyph(source, glyph)

    source = ColumnDataSource(data=dict(t=[(starttime - datetime.now()).seconds], x=[acc.x], y=[acc.y], z=[acc.z]))
    plot.line(x='t', y='x', color='red', source=source, line_width=3)
    plot.line(x='t', y='y', color='green', source=source, line_width=3)
    plot.line(x='t', y='z', color='blue', source=source, line_width=3)

    def update():
        acc = am.measure()
        # print(acc)
        time = int((starttime - datetime.now()).seconds)
        source.stream(dict(t=[time], x=[acc.x], y=[acc.y], z=[acc.z]), rollover=300)

    plot.title.text = "Acceleration"
    plot.xaxis.axis_label = "Time"
    plot.yaxis.axis_label = "Acceleration [m/s^2]"
    document.add_periodic_callback(update, 150)
    document.add_root(plot)
    document.theme = theme


if __name__ == '__main__':
    locations = {
        '/tilt': plot_tilt,
        '/temperature': plot_temperature,
        '/acceleration': plot_acceleration
    }
    server = Server(locations, num_procs=1, allow_websocket_origin=['*'], prefix='plot/')
    server.start()

    print('Opening Bokeh application on http://localhost:5006/')

    server.io_loop.add_callback(server.show, "/")
    server.io_loop.start()
else:
    doc = curdoc()
    plot_tilt(doc)
    plot_acceleration(doc)
    plot_temperature(doc)
