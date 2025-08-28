from enum import Enum


class ProductType(str, Enum):
    NORMAL = "NORMAL"
    SEASONAL = "SEASONAL"
    EXPIRABLE = "EXPIRABLE"
