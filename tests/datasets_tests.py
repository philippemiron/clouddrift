import numpy as np

import tests.utils as testutils
from clouddrift import datasets
from clouddrift.ragged import apply_ragged, subset


class datasets_tests(testutils.DisableProgressTestCase):
    def test_gdp1h(self):
        with datasets.gdp1h() as ds:
            self.assertTrue(ds)

    def test_gdp6h(self):
        with datasets.gdp6h() as ds:
            self.assertTrue(ds)

    def test_glad(self):
        with datasets.glad() as ds:
            self.assertTrue(ds)

    def test_glad_dims_coords(self):
        with datasets.glad() as ds:
            self.assertTrue(len(ds.sizes) == 2)
            self.assertTrue("obs" in ds.dims)
            self.assertTrue("traj" in ds.dims)
            self.assertTrue(len(ds.coords) == 2)
            self.assertTrue("time" in ds.coords)
            self.assertTrue("id" in ds.coords)

    def test_glad_subset_and_apply_ragged_work(self):
        with datasets.glad() as ds:
            ds_sub = subset(
                ds,
                {"id": ["CARTHE_001", "CARTHE_002"]},
                id_var_name="id",
                row_dim_name="traj",
            )
            self.assertTrue(ds_sub)
            mean_lon = apply_ragged(np.mean, [ds_sub.longitude], ds_sub.rowsize)
            self.assertTrue(mean_lon.size == 2)

    def test_spotters_opens(self):
        with datasets.spotters() as ds:
            self.assertTrue(ds)

    def test_subsurface_floats_opens(self):
        with datasets.subsurface_floats() as ds:
            self.assertTrue(ds)

    def test_andro_opens(self):
        with datasets.andro() as ds:
            self.assertTrue(ds is not None)
            self.assertTrue(len(ds.variables) > 0)
            self.assertTrue(len(ds["lon_d"]) > 0)

            self.assertTrue(
                len(ds.lat_d[np.logical_or(ds.lat_d > 90, ds.lat_d < -90)]) == 0
            )
            self.assertTrue(
                len(ds.lat_d[np.logical_or(ds.lon_d > 180, ds.lon_d < -180)]) == 0
            )

    def test_yomaha_opens(self):
        with datasets.yomaha() as ds:
            self.assertTrue(ds)

    def test_mosaic_opens(self):
        with datasets.mosaic() as ds:
            self.assertTrue(ds)
