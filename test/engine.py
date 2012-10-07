# -*- coding: utf-8 -*-

from kivyparticle import ParticleSystem
from kivy.graphics.opengl import GL_ONE, GL_SRC_ALPHA
import unittest
import math


class TestParticleSystem(unittest.TestCase):
    def setUp(self):
        self.s = ParticleSystem('test/media/config.pex')

    def test_config(self):
        self.assertEquals((32, 32), self.s.texture.size)
        self.assertEquals(160.55, self.s.emitter_x)
        self.assertEquals(428.95, self.s.emitter_y)
        self.assertEquals(104.41, self.s.emitter_x_variance)
        self.assertEquals(0.00, self.s.emitter_y_variance)
        self.assertEquals(0.00, self.s.gravity_x)
        self.assertEquals(0.00, self.s.gravity_y)
        self.assertEquals(0, self.s.emitter_type)
        self.assertEquals(300, self.s.max_num_particles)
        self.assertEquals(2.0, self.s.life_span)
        self.assertEquals(1.9, self.s.life_span_variance)
        self.assertEquals(70.0, self.s.start_size)
        self.assertEquals(49.53, self.s.start_size_variance)
        self.assertEquals(10.0, self.s.end_size)
        self.assertEquals(0.0, self.s.end_size_variance)
        self.assertEquals(math.radians(270.37), self.s.emit_angle)
        self.assertEquals(math.radians(15.0), self.s.emit_angle_variance)
        self.assertEquals(0.0, self.s.start_rotation)
        self.assertEquals(0.0, self.s.start_rotation_variance)
        self.assertEquals(0.0, self.s.end_rotation)
        self.assertEquals(0.0, self.s.end_rotation_variance)
        self.assertEquals(90.0, self.s.speed)
        self.assertEquals(30.0, self.s.speed_variance)
        self.assertEquals(0.0, self.s.radial_acceleration)
        self.assertEquals(0.0, self.s.radial_acceleration_variance)
        self.assertEquals(0.0, self.s.tangential_acceleration)
        self.assertEquals(0.0, self.s.tangential_acceleration_variance)
        self.assertEquals(100.0, self.s.max_radius)
        self.assertEquals(0.0, self.s.max_radius_variance)
        self.assertEquals(0.0, self.s.min_radius)
        self.assertEquals(0.0, self.s.rotate_per_second)
        self.assertEquals(0.0, self.s.rotate_per_second_variance)
        self.assertEquals([1.0, 0.31, 0.0, 0.62], self.s.start_color)
        self.assertEquals([0.0, 0.0, 0.0, 0.0], self.s.start_color_variance)
        self.assertEquals([1.0, 0.31, 0.0, 0.0], self.s.end_color)
        self.assertEquals([0.0, 0.0, 0.0, 0.0], self.s.end_color_variance)
        self.assertEquals(GL_SRC_ALPHA, self.s.blend_factor_source)
        self.assertEquals(GL_ONE, self.s.blend_factor_dest)
