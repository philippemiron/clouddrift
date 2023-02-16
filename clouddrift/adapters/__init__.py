"""
This module provides adapters to custom datasets.
Each adapter module provides convenience functions and metadata to convert a
custom dataset to a `clouddrift.RaggedArray` instance.
Currently, clouddrift only provides an adapter module for the hourly Global
Drifter Program (GDP) data, and more adapters will be added in the future.
"""

import clouddrift.adapters.gdp