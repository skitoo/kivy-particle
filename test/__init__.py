# -*- coding: utf-8 -*-

import unittest
from .engine import TestParticleSystem

__all__ = ['main']


def main():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestParticleSystem))
    unittest.TextTestRunner(verbosity=2).run(suite)
