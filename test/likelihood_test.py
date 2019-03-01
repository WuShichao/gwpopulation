from __future__ import division

import unittest

import numpy as np
import pandas as pd

try:
    import cupy as xp
except ImportError:
    xp = np

from gwpopulation.hyperpe import HyperparameterLikelihood, RateLikelihood


class Likelihoods(unittest.TestCase):

    def setUp(self):
        self.params = dict(a=1, b=1, c=1)
        self.model = lambda x, a, b, c: x['a']
        self.sampling_prior = lambda x: 1
        one_data = pd.DataFrame({key: xp.ones(500) for key in self.params})
        self.data = [one_data] * 5
        self.ln_evidences = [0] * 5
        self.selection_function=lambda args: 2
        self.conversion_function=lambda args: (args, ['bar'])

    def tearDown(self):
        pass

    def test_hpe_likelihood_requires_posteriors(self):
        with self.assertRaises(TypeError):
            like = HyperparameterLikelihood(
                hyper_prior=self.model, sampling_prior=self.sampling_prior)

    def test_hpe_likelihood_requires_hyper_prior(self):
        with self.assertRaises(TypeError):
            like = HyperparameterLikelihood(
                posteriors=self.data, sampling_prior=self.sampling_prior)

    def test_likelihood_requires_sampling_prior(self):
        with self.assertRaises(TypeError):
            like = HyperparameterLikelihood(
                posteriors=self.data, hyper_prior=self.model)

    def test_hpe_likelihood_set_evidences(self):
        like = HyperparameterLikelihood(
            posteriors=self.data, hyper_prior=self.model,
            sampling_prior=self.sampling_prior,
            ln_evidences=self.ln_evidences)
        self.assertEqual(like.total_noise_evidence, 0)

    def test_hpe_likelihood_dont_set_evidences(self):
        like = HyperparameterLikelihood(
            posteriors=self.data, hyper_prior=self.model,
            sampling_prior=self.sampling_prior)
        self.assertTrue(xp.isnan(like.total_noise_evidence))

    def test_hpe_likelihood_set_conversion(self):
        like = HyperparameterLikelihood(
            posteriors=self.data, hyper_prior=self.model,
            sampling_prior=self.sampling_prior,
            conversion_function=self.conversion_function)
        self.assertEqual(like.conversion_function('foo'), ('foo', ['bar']))

    def test_hpe_likelihood_set_selection(self):
        like = HyperparameterLikelihood(
            posteriors=self.data, hyper_prior=self.model,
            sampling_prior=self.sampling_prior,
            selection_function=self.selection_function)
        self.assertEqual(like.selection_function('foo'), 2.0)

    def test_hpe_likelihood_set_max_samples(self):
        like = HyperparameterLikelihood(
            posteriors=self.data, hyper_prior=self.model,
            sampling_prior=self.sampling_prior,
            max_samples=10)
        self.assertEqual(like.data['a'].shape, (5, 10))

    def test_hpe_likelihood_log_likelihood_ratio(self):
        like = HyperparameterLikelihood(
            posteriors=self.data, hyper_prior=self.model,
            sampling_prior=self.sampling_prior)
        like.parameters.update(self.params)
        self.assertEqual(like.log_likelihood_ratio(), -5.0)

    def test_hpe_likelihood_noise_likelihood_ratio(self):
        like = HyperparameterLikelihood(
            posteriors=self.data, hyper_prior=self.model,
            sampling_prior=self.sampling_prior,
            selection_function=self.selection_function,
            ln_evidences=self.ln_evidences)
        like.parameters.update(self.params)
        self.assertEqual(like.noise_log_likelihood(), 0)

    def test_hpe_likelihood_log_likelihood_equal_ratio_zero_evidence(self):
        like = HyperparameterLikelihood(
            posteriors=self.data, hyper_prior=self.model,
            sampling_prior=self.sampling_prior,
            selection_function=self.selection_function,
            ln_evidences=self.ln_evidences)
        like.parameters.update(self.params)
        self.assertEqual(like.log_likelihood_ratio(), like.log_likelihood())

    def test_hpe_likelihood_conversion_function_pops_parameters(self):
        like = HyperparameterLikelihood(
            posteriors=self.data, hyper_prior=self.model,
            sampling_prior=self.sampling_prior,
            conversion_function=self.conversion_function,
            selection_function=self.selection_function,
            ln_evidences=self.ln_evidences)
        self.params['bar'] = None
        like.parameters.update(self.params)
        like.log_likelihood_ratio()
        self.assertFalse('bar' in like.parameters)

    def test_rate_likelihood_conversion_function_pops_parameters(self):
        like = RateLikelihood(
            posteriors=self.data, hyper_prior=self.model,
            sampling_prior=self.sampling_prior,
            conversion_function=self.conversion_function,
            selection_function=self.selection_function,
            ln_evidences=self.ln_evidences)
        self.params['bar'] = None
        self.params['rate'] = 1
        like.parameters.update(self.params)
        like.log_likelihood_ratio()
        self.assertFalse('bar' in like.parameters)

    def test_rate_likelihood_requires_rate(self):
        like = RateLikelihood(
            posteriors=self.data, hyper_prior=self.model,
            sampling_prior=self.sampling_prior,
            selection_function=self.selection_function,
            ln_evidences=self.ln_evidences)
        like.parameters.update(self.params)
        with self.assertRaises(KeyError):
            like.log_likelihood_ratio()
