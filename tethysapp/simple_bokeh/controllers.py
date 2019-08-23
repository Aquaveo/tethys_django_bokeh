from os.path import join, dirname, abspath
from typing import Any

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from bokeh.plotting import figure
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, Slider
from bokeh.document import Document
from bokeh.themes import Theme
from bokeh.embed import server_document

from bokeh.sampledata.sea_surface_temperature import sea_surface_temperature

import param
import panel as pn
import numpy as np

theme = Theme(filename=join(dirname(abspath(__file__)), "theme.yaml"))


def home_handler(doc: Document) -> None:
    df = sea_surface_temperature.copy()
    source = ColumnDataSource(data=df)

    plot = figure(x_axis_type="datetime", y_range=(0, 25), y_axis_label="Temperature (Celsius)",
                  title="Sea Surface Temperature at 43.18, -70.43")
    plot.line("time", "temperature", source=source)

    def callback(attr: str, old: Any, new: Any) -> None:
        if new == 0:
            data = df
        else:
            data = df.rolling("{0}D".format(new)).mean()
        source.data = ColumnDataSource(data=data).data

    slider = Slider(start=0, end=30, value=0, step=1, title="Smoothing by N Days")
    slider.on_change("value", callback)

    doc.theme = theme
    doc.add_root(column(slider, plot))


def home(request: HttpRequest) -> HttpResponse:
    script = server_document(request.build_absolute_uri())
    return render(request, 'simple_bokeh/home.html', dict(script=script))


class Shape(param.Parameterized):
    radius = param.Number(default=1, bounds=(0, 1))

    def __init__(self, **params):
        super(Shape, self).__init__(**params)
        self.figure = figure(x_range=(-1, 1), y_range=(-1, 1), width=500, height=500)
        self.renderer = self.figure.line(*self._get_coords())

    def _get_coords(self):
        return [], []

    def view(self):
        return self.figure


class Circle(Shape):
    n = param.Integer(default=100, precedence=-1)

    def __init__(self, **params):
        super(Circle, self).__init__(**params)

    def _get_coords(self):
        angles = np.linspace(0, 2 * np.pi, self.n + 1)
        return (self.radius * np.sin(angles),
                self.radius * np.cos(angles))

    @param.depends('radius', watch=True)
    def update(self):
        xs, ys = self._get_coords()
        self.renderer.data_source.data.update({'x': xs, 'y': ys})


class NGon(Circle):
    n = param.Integer(default=3, bounds=(3, 10), precedence=1)

    @param.depends('radius', 'n', watch=True)
    def update(self):
        xs, ys = self._get_coords()
        self.renderer.data_source.data.update({'x': xs, 'y': ys})


shapes = [NGon(), Circle()]


class ShapeViewer(param.Parameterized):
    shape = param.ObjectSelector(default=shapes[0], objects=shapes)

    @param.depends('shape')
    def view(self):
        return self.shape.view()

    @param.depends('shape', 'shape.radius')
    def title(self):
        return '## %s (radius=%.1f)' % (type(self.shape).__name__, self.shape.radius)

    def panel(self):
        return pn.Column(self.title, self.view)


def shapes_handler(doc: Document) -> None:
    viewer = ShapeViewer()
    panel = pn.Row(viewer.param, viewer.panel())
    panel.server_doc(doc)


def shapes_with_panel(request: HttpRequest) -> HttpResponse:
    script = server_document(request.build_absolute_uri())
    return render(request, "simple_bokeh/shapes.html", dict(script=script))
