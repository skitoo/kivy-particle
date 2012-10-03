import kivy
import sys

sys.path.append('../src')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.core.image import Image
from kivy_particle import PDParticleSystem
from kivy.config import Config

from xml.dom.minidom import parse as parse_xml


class PaintWidget(Widget):
    def __init__(self, **kwargs):
        super(PaintWidget, self).__init__(**kwargs)

        texture = Image('media/particle.png').texture
        self.sun = PDParticleSystem(parse_xml('media/sun.pex'), texture)
        self.drugs = PDParticleSystem(parse_xml('media/drugs.pex'), texture)
        self.jellyfish = PDParticleSystem(parse_xml('media/jellyfish.pex'), texture)
        self.fire = PDParticleSystem(parse_xml('media/particle.pex'), texture)

        self.current = None
        self._show(self.sun)

    def on_touch_down(self, touch):
        self.current.emitter_x = touch.x
        self.current.emitter_y = touch.y

    def on_touch_move(self, touch):
        self.current.emitter_x = touch.x
        self.current.emitter_y = touch.y

    def show_sun(self, b):
        self._show(self.sun)

    def show_drugs(self, b):
        self._show(self.drugs)

    def show_jellyfish(self, b):
        self._show(self.jellyfish)

    def show_fire(self, b):
        self._show(self.fire)

    def _show(self, system):
        if self.current:
            self.remove_widget(self.current)
            self.current.stop(True)
        self.current = system

        self.current.emitter_x = 300
        self.current.emitter_y = 300
        self.add_widget(self.current)
        self.current.start()


class MyPainApp(App):
    def build(self):
        root = GridLayout(cols=2)
        paint = PaintWidget(size_hint_x=None, width=600)
        root.add_widget(paint)
        buttons = BoxLayout(orientation='vertical')
        root.add_widget(buttons)

        sun = Button(text='Sun')
        sun.bind(on_press=paint.show_sun)
        buttons.add_widget(sun)

        drugs = Button(text='Drugs')
        drugs.bind(on_press=paint.show_drugs)
        buttons.add_widget(drugs)

        jellyfish = Button(text='JellyFish')
        jellyfish.bind(on_press=paint.show_jellyfish)
        buttons.add_widget(jellyfish)

        fire = Button(text='Fire')
        fire.bind(on_press=paint.show_fire)
        buttons.add_widget(fire)

        return root


if __name__ == '__main__':
    kivy.require('1.4.0')
    Config.set('modules', 'monitor', '')
    MyPainApp().run()
