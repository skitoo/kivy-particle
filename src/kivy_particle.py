
import kivy
kivy.require('1.4.0')

from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.graphics import Rectangle, Color, Callback
from kivy.graphics.opengl import glBlendFunc, GL_SRC_ALPHA, GL_ONE, GL_ZERO, GL_SRC_COLOR, GL_ONE_MINUS_SRC_COLOR, GL_ONE_MINUS_SRC_ALPHA, GL_DST_ALPHA, GL_ONE_MINUS_DST_ALPHA, GL_DST_COLOR, GL_ONE_MINUS_DST_COLOR

import random
import sys
import math


EMITTER_TYPE_GRAVITY = 0
EMITTER_TYPE_RADIAL = 1

BLEND_FUNC = {0: GL_ZERO,
            1: GL_ONE,
            0x300: GL_SRC_COLOR,
            0x301: GL_ONE_MINUS_SRC_COLOR,
            0x302: GL_SRC_ALPHA,
            0x303: GL_ONE_MINUS_SRC_ALPHA,
            0x304: GL_DST_ALPHA,
            0x305: GL_ONE_MINUS_DST_ALPHA,
            0x306: GL_DST_COLOR,
            0x307: GL_ONE_MINUS_DST_COLOR
}


def random_color():
    return Color(random.random(), random.random(), random.random())


class Particle(object):
    x, y, rotation, current_time = 0, 0, 0, 0
    scale, total_time = 1.0, 1.0
    color = [1.0, 1.0, 1.0, 1.0]


class ParticleSystem(Widget):
    def __init__(self, texture, emission_rate, initial_capacity=128, max_capacity=8192, blend_factor_source=None, blend_factor_dest=None, **kwargs):
        super(ParticleSystem, self).__init__(**kwargs)
        self.texture = texture
        self.emission_rate = emission_rate
        self.initial_capacity = initial_capacity
        self.max_capacity = min(max_capacity, 8192)
        self.blend_factor_source = blend_factor_source
        self.blend_factor_dest = blend_factor_dest

        self.capacity = 0
        self.particles = list()
        self.particles_dict = dict()
        self.emission_time = 0.0
        self.frame_time = 0.0
        self.emitter_x = self.emitter_y = 0.0
        self.num_particles = 0

        self._raise_capacity(self.initial_capacity)

        #self.canvas = RenderContext()
        #with self.canvas:
        #    self.fbo = Fbo(size=self.size)

        Clock.schedule_interval(self._update, 1.0 / 60.0)

    def _update(self, dt):
        self.advance_time(dt)
        self.render()

    def _create_particle(self):
        return Particle()

    def _init_particle(self, particle):
        particle.x = self.emitter_x
        particle.y = self.emitter_y
        particle.current_time = 0.0
        particle.total_time = 1.0
        particle.color = random_color()

    def _advance_particle(self, particle, passed_time):
        particle.y = passed_time * 250
        particle.alpha = 1.0 - particle.current_time / particle.total_time
        particle.scale = 1.0 - particle.alpha
        particle.current_time += passed_time

    def _raise_capacity(self, by_amount):
        old_capacity = self.capacity
        new_capacity = min(self.max_capacity, self.capacity + by_amount)

        for i in range(new_capacity - old_capacity):
            self.particles.append(self._create_particle())

    def start(self, duration=sys.maxint):
        if self.emission_rate != 0:
            self.emission_time = duration

    def stop(self, clear=False):
        self.emission_time = 0.0
        if clear:
            self.num_particles = 0
            self.particles_dict = dict()
            self.canvas.clear()

    def advance_time(self, passed_time):
        particle_index = 0

        # advance existing particles
        while particle_index < self.num_particles:
            particle = self.particles[particle_index]
            if particle.current_time < particle.total_time:
                self._advance_particle(particle, passed_time)
                particle_index += 1
            else:
                if particle_index != self.num_particles - 1:
                    next_particle = self.particles[self.num_particles - 1]
                    self.particles[self.num_particles - 1] = particle
                    self.particles[particle_index] = next_particle

                self.num_particles -= 1
                if self.num_particles == 0:
                    print 'COMPLETE'
                    #self.dispatch('COMPLETE')

        # create and advance new particles
        if self.emission_time > 0:
            time_between_particles = 1.0 / self.emission_rate
            self.frame_time += passed_time

            while self.frame_time > 0:
                if self.num_particles < self.max_capacity:
                    if self.num_particles == self.capacity:
                        self._raise_capacity(self.capacity)

                    particle = self.particles[self.num_particles]
                    self.num_particles += 1
                    self._init_particle(particle)
                    self._advance_particle(particle, self.frame_time)

                self.frame_time -= time_between_particles

            if self.emission_time != sys.maxint:
                self.emission_time = max(0.0, self.emission_time - passed_time)

    def render(self):
        if self.num_particles == 0:
            return
        for i in range(self.num_particles):
            particle = self.particles[i]
            if particle not in self.particles_dict:
                self.particles_dict[particle] = dict()
                with self.canvas:
                    self.particles_dict[particle]['color'] = Color(particle.color[0], particle.color[1], particle.color[2], particle.color[3])
                    self.particles_dict[particle]['rect'] = Rectangle(texture=self.texture, pos=(particle.x, particle.y), size=(self.texture.size[0] * particle.scale, self.texture.size[1] * particle.scale))
            else:
                self.particles_dict[particle]['rect'].pos = (particle.x, particle.y)
                self.particles_dict[particle]['rect'].size = (self.texture.size[0] * particle.scale, self.texture.size[1] * particle.scale)


class PDParticle(Particle):
    color_argb, color_argb_delta = [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0]
    start_x, start_y, velocity_x, velocity_y = 0, 0, 0, 0
    radial_acceleration, tangent_acceleration = 0, 0
    emit_radius, emit_radius_delta = 0, 0
    emit_rotation, emit_rotation_delta = 0, 0
    rotation_delta, scale_delta = 0, 0


class PDParticleSystem(ParticleSystem):
    def __init__(self, config, texture):
        self._parse_config(config)
        emission_rate = self.max_num_particles / self.life_span
        super(PDParticleSystem, self).__init__(texture, emission_rate, self.max_num_particles, self.max_num_particles, self.blend_factor_source, self.blend_factor_dest)
        self.premultiplied_alpha = False

        with self.canvas.before:
            Callback(self._set_blend_func)
        with self.canvas.after:
            Callback(self._reset_blend_func)

    def _set_blend_func(self, instruction):
        glBlendFunc(self.blend_factor_source, self.blend_factor_dest)

    def _reset_blend_func(self, instruction):
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    def _parse_config(self, config):
        self._config = config
        self.emitter_x_variance = float(self._parse_data('sourcePositionVariance', 'x'))
        self.emitter_y_variance = float(self._parse_data('sourcePositionVariance', 'y'))
        self.gravity_x = float(self._parse_data('gravity', 'x'))
        self.gravity_y = float(self._parse_data('gravity', 'y'))
        self.emitter_type = int(self._parse_data('emitterType'))
        self.max_num_particles = int(self._parse_data('maxParticles'))
        self.life_span = max(0.01, float(self._parse_data('particleLifeSpan')))
        self.life_span_variance = float(self._parse_data('particleLifespanVariance'))
        self.start_size = float(self._parse_data('startParticleSize'))
        self.start_size_variance = float(self._parse_data('startParticleSizeVariance'))
        self.end_size = float(self._parse_data('finishParticleSize'))
        self.end_size_variance = float(self._parse_data('FinishParticleSizeVariance'))
        self.emit_angle = math.radians(float(self._parse_data('angle')))
        self.emit_angle_variance = math.radians(float(self._parse_data('angleVariance')))
        self.start_rotation = math.radians(float(self._parse_data('rotationStart')))
        self.start_rotation_variance = math.radians(float(self._parse_data('rotationStartVariance')))
        self.end_rotation = math.radians(float(self._parse_data('rotationEnd')))
        self.end_rotation_variance = math.radians(float(self._parse_data('rotationEndVariance')))
        self.speed = float(self._parse_data('speed'))
        self.speed_variance = float(self._parse_data('speedVariance'))
        self.radial_acceleration = float(self._parse_data('radialAcceleration'))
        self.radial_acceleration_variance = float(self._parse_data('radialAccelVariance'))
        self.tangential_acceleration = float(self._parse_data('tangentialAcceleration'))
        self.tangential_acceleration_variance = float(self._parse_data('tangentialAccelVariance'))
        self.max_radius = float(self._parse_data('maxRadius'))
        self.max_radius_variance = float(self._parse_data('maxRadiusVariance'))
        self.min_radius = float(self._parse_data('minRadius'))
        self.rotate_per_second = math.radians(float(self._parse_data('rotatePerSecond')))
        self.rotate_per_second_variance = math.radians(float(self._parse_data('rotatePerSecondVariance')))
        self.start_color = self._parse_color('startColor')
        self.start_color_variance = self._parse_color('startColorVariance')
        self.end_color = self._parse_color('finishColor')
        self.end_color_variance = self._parse_color('finishColorVariance')
        self.blend_factor_source = self._parse_blend('blendFuncSource')
        self.blend_factor_dest = self._parse_blend('blendFuncDestination')

    def _parse_data(self, name, attribute='value'):
        return self._config.getElementsByTagName(name)[0].getAttribute(attribute)

    def _parse_color(self, name):
        return [float(self._parse_data(name, 'red')), float(self._parse_data(name, 'green')), float(self._parse_data(name, 'blue')), float(self._parse_data(name, 'alpha'))]

    def _parse_blend(self, name):
        value = int(self._parse_data(name))
        return BLEND_FUNC[value]

    def _create_particle(self):
        return PDParticle()

    def _init_particle(self, particle):
        life_span = self.life_span + self.life_span_variance * (random.random() * 2.0 - 1.0)
        if life_span <= 0:
            return

        particle.current_time = 0.0
        particle.total_time = life_span

        particle.x = self.emitter_x + self.emitter_x_variance * (random.random() * 2.0 - 1.0)
        particle.y = self.emitter_y + self.emitter_y_variance * (random.random() * 2.0 - 1.0)
        particle.start_x = self.emitter_x
        particle.start_y = self.emitter_y

        angle = self.emit_angle + self.emit_angle_variance * (random.random() * 2.0 - 1.0)
        speed = self.speed + self.speed_variance * (random.random() * 2.0 - 1.0)
        particle.velocity_x = speed * math.cos(angle)
        particle.velocity_y = speed * math.sin(angle)

        particle.emit_radius = self.max_radius + self.max_radius_variance * (random.random() * 2.0 - 1.0)
        particle.emit_radius_delta = self.max_radius / life_span

        particle.emit_rotation = self.emit_angle + self.emit_angle_variance * (random.random() * 2.0 - 1.0)
        particle.emit_rotation_delta = self.rotate_per_second + self.rotate_per_second_variance * (random.random() * 2.0 - 1.0)

        particle.radial_acceleration = self.radial_acceleration + self.radial_acceleration_variance * (random.random() * 2.0 - 1.0)
        particle.tangent_acceleration = self.tangential_acceleration + self.tangential_acceleration_variance * (random.random() * 2.0 - 1.0)

        start_size = self.start_size + self.start_size_variance * (random.random() * 2.0 - 1.0)
        end_size = self.end_size + self.end_size_variance * (random.random() * 2.0 - 1.0)

        if start_size < 0.1:
            start_size = 0.1
        if end_size < 0.1:
            end_size = 0.1

        particle.scale = start_size / self.texture.width
        particle.scale_delta = ((end_size - start_size) / life_span) / self.texture.width

        # colors

        particle.color_argb = self.start_color[:]
        for i in range(4):
            if self.start_color_variance[i] != 0:
                particle.color_argb[i] += self.start_color_variance[i] * (random.random() * 2.0 - 1.0)

        end_color = self.end_color[:]
        for i in range(4):
            if self.end_color_variance[i] != 0:
                end_color[i] += self.end_color_variance[i] * (random.random() * 2.0 - 1.0)
            particle.color_argb_delta[i] = (end_color[i] - self.start_color[i]) / life_span

        # rotation
        start_rotation = self.start_rotation + self.start_rotation_variance * (random.random() * 2.0 - 1.0)
        end_rotation = self.end_rotation + self.end_rotation_variance * (random.random() * 2.0 - 1.0)
        particle.rotation = start_rotation
        particle.rotation_delta = (end_rotation - start_rotation) / life_span

    def _advance_particle(self, particle, passed_time):
        rest_time = particle.total_time - particle.current_time
        if rest_time <= passed_time:
            passed_time = rest_time
        particle.current_time += passed_time

        if self.emitter_type == EMITTER_TYPE_RADIAL:
            particle.emit_rotation += particle.emit_rotation_delta * passed_time
            particle.emit_radius -= particle.emit_radius_delta * passed_time
            particle.x = self.emitter_x - math.cos(particle.emit_rotation) * particle.emit_radius
            particle.y = self.emitter_y - math.sin(particle.emit_rotation) * particle.emit_radius

            if particle.emit_radius < self.min_radius:
                particle.current_time = particle.total_time

        else:
            distance_x = particle.x - particle.start_x
            distance_y = particle.y - particle.start_y
            distance_scalar = math.sqrt(distance_x * distance_x + distance_y * distance_y)
            if distance_scalar < 0.01:
                distance_scalar = 0.01

            radial_x = distance_x / distance_scalar
            radial_y = distance_y / distance_scalar
            tangential_x = radial_x
            tangential_y = radial_y

            radial_x *= particle.radial_acceleration
            radial_y *= particle.radial_acceleration

            new_y = tangential_x
            tangential_x = -tangential_y * particle.tangent_acceleration
            tangential_y = new_y * particle.tangent_acceleration

            particle.velocity_x += passed_time * (self.gravity_x + radial_x + tangential_x)
            particle.velocity_y += passed_time * (self.gravity_y + radial_y + tangential_y)

            particle.x += particle.velocity_x * passed_time
            particle.y += particle.velocity_y * passed_time

        particle.scale += particle.scale_delta * passed_time
        particle.rotation += particle.rotation_delta * passed_time

        for i in range(4):
            particle.color_argb[i] += particle.color_argb_delta[i] * passed_time

        particle.color = particle.color_argb
