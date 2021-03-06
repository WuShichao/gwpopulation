import unittest

import numpy as np

from bilby.core.prior import PriorDict, Uniform

from gwpopulation.cupy_utils import trapz, xp
from gwpopulation.models import mass


class TestDoublePowerLaw(unittest.TestCase):

    def setUp(self):
        self.m1s = np.linspace(3, 100, 1000)
        self.qs = np.linspace(0.01, 1, 500)
        m1s_grid, qs_grid = xp.meshgrid(self.m1s, self.qs)
        self.dataset = dict(mass_1=m1s_grid, mass_ratio=qs_grid)
        self.power_prior = PriorDict()
        self.power_prior['alpha_1'] = Uniform(minimum=-4, maximum=12)
        self.power_prior['alpha_2'] = Uniform(minimum=-4, maximum=12)
        self.power_prior['beta'] = Uniform(minimum=-4, maximum=12)
        self.power_prior['mmin'] = Uniform(minimum=3, maximum=10)
        self.power_prior['mmax'] = Uniform(minimum=40, maximum=100)
        self.power_prior['break_fraction'] = Uniform(minimum=40, maximum=100)
        self.n_test = 10

    def test_double_power_law_zero_below_mmin(self):
        for ii in range(self.n_test):
            parameters = self.power_prior.sample()
            del parameters['beta']
            p_m = mass.double_power_law_primary_mass(self.m1s, **parameters)
            self.assertEqual(xp.max(p_m[self.m1s <= parameters['mmin']]), 0.0)

    def test_power_law_primary_mass_ratio_zero_above_mmax(self):
        for ii in range(self.n_test):
            parameters = self.power_prior.sample()
            p_m = mass.double_power_law_primary_power_law_mass_ratio(
                self.dataset, **parameters)
            self.assertEqual(
                xp.max(p_m[self.dataset['mass_1'] >= parameters['mmax']]), 0.0)


class TestPrimaryMassRatio(unittest.TestCase):

    def setUp(self):
        self.m1s = np.linspace(3, 100, 1000)
        self.qs = np.linspace(0.01, 1, 500)
        m1s_grid, qs_grid = xp.meshgrid(self.m1s, self.qs)
        self.dataset = dict(mass_1=m1s_grid, mass_ratio=qs_grid)
        self.power_prior = PriorDict()
        self.power_prior['alpha'] = Uniform(minimum=-4, maximum=12)
        self.power_prior['beta'] = Uniform(minimum=-4, maximum=12)
        self.power_prior['mmin'] = Uniform(minimum=3, maximum=10)
        self.power_prior['mmax'] = Uniform(minimum=40, maximum=100)
        self.gauss_prior = PriorDict()
        self.gauss_prior['lam'] = Uniform(minimum=0, maximum=1)
        self.gauss_prior['mpp'] = Uniform(minimum=20, maximum=60)
        self.gauss_prior['sigpp'] = Uniform(minimum=0, maximum=10)
        self.n_test = 10

    def test_power_law_primary_mass_ratio_zero_below_mmin(self):
        m2s = self.dataset['mass_1'] * self.dataset['mass_ratio']
        for ii in range(self.n_test):
            parameters = self.power_prior.sample()
            p_m = mass.power_law_primary_mass_ratio(self.dataset, **parameters)
            self.assertEqual(xp.max(p_m[m2s <= parameters['mmin']]), 0.0)

    def test_power_law_primary_mass_ratio_zero_above_mmax(self):
        for ii in range(self.n_test):
            parameters = self.power_prior.sample()
            p_m = mass.power_law_primary_mass_ratio(self.dataset, **parameters)
            self.assertEqual(
                xp.max(p_m[self.dataset['mass_1'] >= parameters['mmax']]), 0.0)

    def test_two_component_primary_mass_ratio_zero_below_mmin(self):
        m2s = self.dataset['mass_1'] * self.dataset['mass_ratio']
        for ii in range(self.n_test):
            parameters = self.power_prior.sample()
            parameters.update(self.gauss_prior.sample())
            p_m = mass.two_component_primary_mass_ratio(
                self.dataset, **parameters)
            self.assertEqual(xp.max(p_m[m2s <= parameters['mmin']]), 0.0)


class TestPrimarySecondary(unittest.TestCase):

    def setUp(self):
        self.ms = np.linspace(3, 100, 1000)
        self.dm = self.ms[1] - self.ms[0]
        m1s_grid, m2s_grid = xp.meshgrid(self.ms, self.ms)
        self.dataset = dict(mass_1=m1s_grid, mass_2=m2s_grid)
        self.power_prior = PriorDict()
        self.power_prior['alpha'] = Uniform(minimum=-4, maximum=12)
        self.power_prior['beta'] = Uniform(minimum=-4, maximum=12)
        self.power_prior['mmin'] = Uniform(minimum=3, maximum=10)
        self.power_prior['mmax'] = Uniform(minimum=40, maximum=100)
        self.gauss_prior = PriorDict()
        self.gauss_prior['lam'] = Uniform(minimum=0, maximum=1)
        self.gauss_prior['mpp'] = Uniform(minimum=20, maximum=60)
        self.gauss_prior['sigpp'] = Uniform(minimum=0, maximum=10)
        self.n_test = 10

    def test_power_law_primary_secondary_zero_below_mmin(self):
        for ii in range(self.n_test):
            parameters = self.power_prior.sample()
            p_m = mass.power_law_primary_secondary_independent(
                self.dataset, **parameters)
            self.assertEqual(
                xp.max(p_m[self.dataset['mass_2'] <= parameters['mmin']]), 0.0)

    def test_power_law_primary_secondary_zero_above_mmax(self):
        for ii in range(self.n_test):
            parameters = self.power_prior.sample()
            del parameters['beta']
            p_m = mass.power_law_primary_secondary_identical(
                self.dataset, **parameters)
            self.assertEqual(
                xp.max(p_m[self.dataset['mass_1'] >= parameters['mmax']]), 0.0)

    def test_two_component_primary_secondary_zero_below_mmin(self):
        for ii in range(self.n_test):
            parameters = self.power_prior.sample()
            parameters.update(self.gauss_prior.sample())
            del parameters['beta']
            p_m = mass.two_component_primary_secondary_identical(
                self.dataset, **parameters)
            self.assertEqual(
                xp.max(p_m[self.dataset['mass_2'] <= parameters['mmin']]), 0.0)


class TestSmoothedMassDistribution(unittest.TestCase):

    def setUp(self):
        self.m1s = np.linspace(3, 100, 1000)
        self.qs = np.linspace(0.01, 1, 500)
        self.dm = self.m1s[1] - self.m1s[0]
        self.dq = self.qs[1] - self.qs[0]
        m1s_grid, qs_grid = xp.meshgrid(self.m1s, self.qs)
        self.dataset = dict(mass_1=m1s_grid, mass_ratio=qs_grid)
        self.power_prior = PriorDict()
        self.power_prior['alpha'] = Uniform(minimum=-4, maximum=12)
        self.power_prior['beta'] = Uniform(minimum=-4, maximum=12)
        self.power_prior['mmin'] = Uniform(minimum=3, maximum=10)
        self.power_prior['mmax'] = Uniform(minimum=30, maximum=100)
        self.gauss_prior = PriorDict()
        self.gauss_prior['lam'] = Uniform(minimum=0, maximum=1)
        self.gauss_prior['mpp'] = Uniform(minimum=20, maximum=60)
        self.gauss_prior['sigpp'] = Uniform(minimum=0, maximum=10)
        self.smooth_prior = PriorDict()
        self.smooth_prior['delta_m'] = Uniform(minimum=0, maximum=10)
        self.n_test = 10

    def test_delta_m_zero_matches_two_component_primary_mass_ratio(self):
        max_diffs = list()
        for ii in range(self.n_test):
            parameters = self.power_prior.sample()
            parameters.update(self.gauss_prior.sample())
            p_m1 = mass.two_component_primary_mass_ratio(
                self.dataset, **parameters)
            parameters['delta_m'] = 0
            p_m2 = mass.smoothed_two_component_primary_mass_ratio(
                self.dataset, **parameters)
            max_diffs.append(_max_abs_difference(p_m1, p_m2))
        self.assertAlmostEqual(max(max_diffs), 0.0)

    def test_normalised(self):
        norms = list()
        for ii in range(self.n_test):
            parameters = self.power_prior.sample()
            parameters.update(self.gauss_prior.sample())
            parameters.update(self.smooth_prior.sample())
            p_m = mass.smoothed_two_component_primary_mass_ratio(
                self.dataset, **parameters)
            norms.append(trapz(trapz(p_m, self.m1s), self.qs))
        self.assertAlmostEqual(_max_abs_difference(norms, 1.0), 0.0, 2)


def _max_abs_difference(array, comparison):
    return float(xp.max(xp.abs(comparison - xp.asarray(array))))
