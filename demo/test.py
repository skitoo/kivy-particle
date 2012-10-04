#import kivy
import sys

sys.path.append('../src')
from kivy.app import App
from kivy.uix.widget import Widget
#from kivy.graphics import Color, Ellipse
from kivy_particle import PDParticleSystem
from kivy.core.image import Image
from xml.dom.minidom import parse as parse_xml


class MyWidget(Widget):
    def __init__(self, **kwargs):
        super(MyWidget, self).__init__(**kwargs)
        texture = Image('media/particle.png').texture
        s = PDParticleSystem(parse_xml('media/fire.pex'), texture)
        self.add_widget(s)
        s.emitter_x = 300
        s.emitter_y = 300
        s.start()


class MyApp(App):
    def build(self):
        return MyWidget()


if __name__ == '__main__':
    MyApp().run()
