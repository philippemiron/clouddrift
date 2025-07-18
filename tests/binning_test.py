import unittest

import numpy as np

from clouddrift.binning import DEFAULT_BINS_NUMBER, binned_statistics


class binning_tests(unittest.TestCase):
    def setUp(self):
        self.coords_1d = np.array(
            [-0.2, 0.3, 0.6, 0.7, 1.2, 1.3, 1.8, 2.1, 2.7, 2.8, 3.1]
        )
        self.bins_range_1d = (0, 3)

        self.coords_2d = [self.coords_1d, self.coords_1d]
        self.bins_range_2d = [(0, 3), (0, 3)]

        self.coords_3d = [self.coords_1d, self.coords_1d, self.coords_1d]
        self.bins_range_3d = [(0, 3), (0, 3), (0, 3)]

        # example with 8 regions around x=[-1,0,1], y=[-1,0,1], z=[-1,0,1]
        self.coords_3d_ex = [[], [], []]
        self.values_3d_ex = []
        for x in [-0.5, -0.25, 0.25, 0.5]:
            for y in [-0.5, -0.25, 0.25, 0.5]:
                for z in [-0.5, -0.25, 0.25, 0.5]:
                    self.coords_3d_ex[0].append(x)
                    self.coords_3d_ex[1].append(y)
                    self.coords_3d_ex[2].append(z)
                    self.values_3d_ex.append(int(x > 0) + int(y > 0) + int(z > 0))

    def test_parameters_dimensions(self):
        with self.assertRaises(ValueError):
            binned_statistics(self.coords_1d, dim_names=["x", "y"])

        with self.assertRaises(ValueError):
            binned_statistics(self.coords_1d, bins=[10, 10])

        with self.assertRaises(ValueError):
            binned_statistics(self.coords_2d, bins=[10])

        with self.assertRaises(ValueError):
            binned_statistics(self.coords_2d, dim_names=["x"])

        with self.assertRaises(ValueError):
            binned_statistics(self.coords_1d, output_names=["x", "y"])

        with self.assertRaises(ValueError):
            binned_statistics(
                self.coords_1d,
                data=np.ones_like(self.coords_1d),
                output_names=["x", "y"],
            )

    def test_bins_number_default(self):
        ds = binned_statistics(self.coords_1d)
        self.assertEqual(len(ds.dim_0_bin), DEFAULT_BINS_NUMBER)

        ds = binned_statistics(self.coords_2d)
        for v in ds.sizes.values():
            self.assertEqual(v, DEFAULT_BINS_NUMBER)

        ds = binned_statistics(self.coords_3d, bins=5)
        for v in ds.sizes.values():
            self.assertEqual(v, 5)

        ds = binned_statistics(self.coords_2d, bins=(5, None))
        self.assertEqual(len(ds.dim_0_bin), 5)
        self.assertEqual(len(ds.dim_1_bin), DEFAULT_BINS_NUMBER)

    def test_1d_hist_number(self):
        ds = binned_statistics(self.coords_1d, bins=3)
        self.assertEqual(len(ds.dim_0_bin), 3)

    def test_2d_hist_number(self):
        ds = binned_statistics(self.coords_2d, bins=(3, 4))
        self.assertEqual(len(ds.dim_0_bin), 3)
        self.assertEqual(len(ds.dim_1_bin), 4)

    def test_3d_hist_number(self):
        ds = binned_statistics(self.coords_3d, bins=(3, 4, 5))
        self.assertEqual(len(ds.dim_0_bin), 3)
        self.assertEqual(len(ds.dim_1_bin), 4)
        self.assertEqual(len(ds.dim_2_bin), 5)

    def test_hist_center(self):
        for i in range(1, 10):
            ds = binned_statistics(self.coords_1d, bins=i)

            bins_coords = np.linspace(
                np.min(self.coords_1d), np.max(self.coords_1d), i + 1
            )
            bins_center = (bins_coords[:-1] + bins_coords[1:]) / 2

            self.assertIsNone(
                np.testing.assert_allclose(ds.dim_0_bin.values, bins_center)
            )

    def test_1d_output(self):
        ds = binned_statistics(coords=self.coords_1d)
        self.assertEqual(len(ds.dim_0_bin), DEFAULT_BINS_NUMBER)
        self.assertEqual(sum(ds["binned_count"].values), len(self.coords_1d))

    def test_1d_output_bins(self):
        n_bins = 3
        ds = binned_statistics(coords=self.coords_1d, bins=n_bins)
        self.assertEqual(len(ds.dim_0_bin), n_bins)
        self.assertEqual(sum(ds["binned_count"].values), len(self.coords_1d))
        self.assertEqual(len(ds["binned_count"].shape), 1)

    def test_1d_output_variables_mean(self):
        value_1 = 1
        value_2 = 2
        variable = [
            np.ones_like(self.coords_1d) * value_1,
            np.ones_like(self.coords_1d) * value_2,
        ]
        ds = binned_statistics(coords=self.coords_1d, data=variable, bins=2)
        self.assertEqual(len(ds.data_vars), 4)
        self.assertTrue(all(ds["binned_mean_0"] == value_1))
        self.assertTrue(all(ds["binned_mean_1"] == value_2))

        coords_threshold = 1
        variables = np.ones_like(self.coords_1d) * value_1
        variables[self.coords_1d > coords_threshold] = value_2
        ds = binned_statistics(
            coords=self.coords_1d,
            data=variables,
            bins=3,
            bins_range=(0, 3),
        )
        mask = ds.dim_0_bin.values < coords_threshold
        self.assertTrue(all(ds["binned_mean_0"].values[mask] == value_1))
        self.assertTrue(all(ds["binned_mean_0"].values[~mask] == value_2))

    def test_2d_output(self):
        ds = binned_statistics(coords=self.coords_2d)
        for v in ds.sizes.values():
            self.assertEqual(v, DEFAULT_BINS_NUMBER)
        self.assertEqual(len(ds["binned_count"].shape), 2)

        n_bins = (3, 4)
        ds = binned_statistics(coords=self.coords_2d, bins=n_bins)
        for i, v in enumerate(ds.sizes.values()):
            self.assertEqual(v, n_bins[i])
        self.assertEqual(len(ds["binned_count"].shape), 2)

        n_bins = (3, None)
        ds = binned_statistics(coords=self.coords_2d, bins=n_bins)
        for i, v in enumerate(ds.sizes.values()):
            self.assertEqual(
                v, n_bins[i] if n_bins[i] is not None else DEFAULT_BINS_NUMBER
            )
        self.assertEqual(len(ds["binned_count"].shape), 2)

    def test_3d_output(self):
        ds = binned_statistics(coords=self.coords_3d)
        for v in ds.sizes.values():
            self.assertEqual(v, DEFAULT_BINS_NUMBER)
        self.assertEqual(len(ds["binned_count"].shape), 3)

        n_bins = (3, 4, 5)
        ds = binned_statistics(coords=self.coords_3d, bins=n_bins)
        for i, v in enumerate(ds.sizes.values()):
            self.assertEqual(v, n_bins[i])
        self.assertEqual(len(ds["binned_count"].shape), 3)

        n_bins = (3, 4, None)
        ds = binned_statistics(coords=self.coords_3d, bins=n_bins)
        for i, v in enumerate(ds.sizes.values()):
            self.assertEqual(
                v, n_bins[i] if n_bins[i] is not None else DEFAULT_BINS_NUMBER
            )
        self.assertEqual(len(ds["binned_count"].shape), 3)

    def test_3d_output_mean_example(self):
        ds = binned_statistics(
            coords=self.coords_3d_ex,
            data=self.values_3d_ex,
            bins=(2, 2, 2),
            bins_range=[(-1, 1), (-1, 1), (-1, 1)],
        )
        self.assertEqual(len(ds.data_vars), 2)
        self.assertIsNone(
            np.testing.assert_allclose(
                ds["binned_mean_0"].values.flatten(),
                np.array(
                    [
                        0,  # (-1, -1, -1)
                        1,  # (-1, -1, 0)
                        1,  # (-1, 0, -1)
                        2,  # (-1, 0, 0)
                        1,  # (0, -1, -1)
                        2,  # (0, -1, 0)
                        2,  # (0, 0, -1)
                        3,  # (0, 0, 0)
                    ]
                ),
            )
        )

    def test_hist_range(self):
        ds = binned_statistics(
            coords=self.coords_1d, bins=3, bins_range=self.bins_range_1d
        )
        self.assertEqual(
            sum(ds["binned_count"].values),
            len(
                self.coords_1d[
                    np.logical_and(
                        self.coords_1d >= self.bins_range_1d[0],
                        self.coords_1d < self.bins_range_1d[1],
                    )
                ]
            ),
        )

    def test_hist_range_2d(self):
        ds = binned_statistics(
            coords=self.coords_2d, bins=(3, 3), bins_range=self.bins_range_2d
        )
        self.assertEqual(
            sum(ds["binned_count"].values.flatten()),
            len(
                self.coords_1d[
                    np.logical_and(
                        self.coords_1d >= self.bins_range_1d[0],
                        self.coords_1d < self.bins_range_1d[1],
                    )
                ]
            ),
        )

    def test_hist_range_3d(self):
        ds = binned_statistics(
            coords=self.coords_3d, bins=(3, 3, 3), bins_range=self.bins_range_3d
        )
        self.assertEqual(
            sum(ds["binned_count"].values.flatten()),
            len(
                self.coords_1d[
                    np.logical_and(
                        self.coords_1d >= self.bins_range_1d[0],
                        self.coords_1d < self.bins_range_1d[1],
                    )
                ]
            ),
        )

    def test_rename_dimensions(self):
        ds = binned_statistics(
            coords=self.coords_1d,
            bins=4,
            dim_names=["x"],
        )
        self.assertIn("x", ds.sizes)

        ds = binned_statistics(
            coords=self.coords_2d,
            bins=(3, 4),
            dim_names=["x", "y"],
        )
        self.assertIn("x", ds.sizes)
        self.assertIn("y", ds.sizes)

    def test_rename_variables(self):
        ds = binned_statistics(
            coords=self.coords_1d,
            bins=4,
            output_names=["mean_x"],
        )
        self.assertIn("mean_x", ds.data_vars)

        ds = binned_statistics(
            coords=self.coords_2d,
            data=[self.coords_1d, self.coords_1d],
            output_names=["mean_x", "mean_y"],
        )
        self.assertIn("mean_x", ds.data_vars)
        self.assertIn("mean_y", ds.data_vars)

    def test_zeros_to_nan(self):
        ds = binned_statistics(coords=self.coords_1d, bins=4, bins_range=(-1, 0))
        empty_bins = ds["binned_count"].values == 0

        ds = binned_statistics(
            coords=self.coords_1d, bins=4, bins_range=(-1, 0), zeros_to_nan=True
        )
        self.assertTrue(np.isnan(ds["binned_count"].values[empty_bins]).all())
