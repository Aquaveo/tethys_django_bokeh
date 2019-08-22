from tethys_sdk.base import TethysAppBase, url_map_maker

class SimpleBokeh(TethysAppBase):
    """
    Tethys app class for Simple Bokeh.
    """

    name = 'Simple Bokeh'
    index = 'simple_bokeh:home'
    icon = 'simple_bokeh/images/icon.gif'
    package = 'simple_bokeh'
    root_url = 'simple-bokeh'
    color = '#2980b9'
    description = ''
    tags = ''
    enable_feedback = False
    feedback_emails = []

    def url_maps(self):
        """
        Add controllers
        """
        UrlMap = url_map_maker(self.root_url)

        url_maps = (
            UrlMap(
                name='home',
                url='simple-bokeh',
                controller='simple_bokeh.controllers.home',
                handler='simple_bokeh.controllers.home_handler',
                handler_type='bokeh'
            ),
            UrlMap(
                name='shapes',
                url='simple-bokeh/shapes',
                controller='simple_bokeh.controllers.shapes_with_panel',
                handler='simple_bokeh.controllers.shapes_handler',
                handler_type='bokeh'
            ),
        )

        return url_maps
