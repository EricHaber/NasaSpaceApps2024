from __future__ import annotations

import enum
from typing import TYPE_CHECKING
from typing import Any
from typing import NoReturn

from narwhals.utils import parse_version

if TYPE_CHECKING:
    import pandas as pd
    import pyarrow as pa
    from typing_extensions import Self

    from narwhals._interchange.series import InterchangeSeries
    from narwhals.dtypes import DType
    from narwhals.typing import DTypes


class DtypeKind(enum.IntEnum):
    # https://data-apis.org/dataframe-protocol/latest/API.html
    INT = 0
    UINT = 1
    FLOAT = 2
    BOOL = 20
    STRING = 21  # UTF-8
    DATETIME = 22
    CATEGORICAL = 23


def map_interchange_dtype_to_narwhals_dtype(
    interchange_dtype: tuple[DtypeKind, int, Any, Any], dtypes: DTypes
) -> DType:
    if interchange_dtype[0] == DtypeKind.INT:
        if interchange_dtype[1] == 64:
            return dtypes.Int64()
        if interchange_dtype[1] == 32:
            return dtypes.Int32()
        if interchange_dtype[1] == 16:
            return dtypes.Int16()
        if interchange_dtype[1] == 8:
            return dtypes.Int8()
        msg = "Invalid bit width for INT"  # pragma: no cover
        raise AssertionError(msg)
    if interchange_dtype[0] == DtypeKind.UINT:
        if interchange_dtype[1] == 64:
            return dtypes.UInt64()
        if interchange_dtype[1] == 32:
            return dtypes.UInt32()
        if interchange_dtype[1] == 16:
            return dtypes.UInt16()
        if interchange_dtype[1] == 8:
            return dtypes.UInt8()
        msg = "Invalid bit width for UINT"  # pragma: no cover
        raise AssertionError(msg)
    if interchange_dtype[0] == DtypeKind.FLOAT:
        if interchange_dtype[1] == 64:
            return dtypes.Float64()
        if interchange_dtype[1] == 32:
            return dtypes.Float32()
        msg = "Invalid bit width for FLOAT"  # pragma: no cover
        raise AssertionError(msg)
    if interchange_dtype[0] == DtypeKind.BOOL:
        return dtypes.Boolean()
    if interchange_dtype[0] == DtypeKind.STRING:
        return dtypes.String()
    if interchange_dtype[0] == DtypeKind.DATETIME:
        return dtypes.Datetime()
    if interchange_dtype[0] == DtypeKind.CATEGORICAL:  # pragma: no cover
        # upstream issue: https://github.com/ibis-project/ibis/issues/9570
        return dtypes.Categorical()
    msg = f"Invalid dtype, got: {interchange_dtype}"  # pragma: no cover
    raise AssertionError(msg)


class InterchangeFrame:
    def __init__(self, df: Any, dtypes: DTypes) -> None:
        self._native_frame = df
        self._interchange_frame = df.__dataframe__()
        self._dtypes = dtypes

    def __narwhals_dataframe__(self) -> Any:
        return self

    def __getitem__(self, item: str) -> InterchangeSeries:
        from narwhals._interchange.series import InterchangeSeries

        return InterchangeSeries(
            self._interchange_frame.get_column_by_name(item), dtypes=self._dtypes
        )

    @property
    def schema(self) -> dict[str, DType]:
        return {
            column_name: map_interchange_dtype_to_narwhals_dtype(
                self._interchange_frame.get_column_by_name(column_name).dtype,
                self._dtypes,
            )
            for column_name in self._interchange_frame.column_names()
        }

    def to_pandas(self: Self) -> pd.DataFrame:
        import pandas as pd  # ignore-banned-import()

        if parse_version(pd.__version__) >= parse_version("1.5.0"):
            return pd.api.interchange.from_dataframe(self._native_frame)
        else:  # pragma: no cover
            msg = (
                "Conversion to pandas is achieved via interchange protocol which requires"
                f" pandas>=1.5.0 to be installed, found {pd.__version__}"
            )
            raise NotImplementedError(msg)

    def to_arrow(self: Self) -> pa.Table:
        from pyarrow.interchange import from_dataframe  # ignore-banned-import()

        return from_dataframe(self._native_frame)

    def __getattr__(self, attr: str) -> NoReturn:
        msg = (
            f"Attribute {attr} is not supported for metadata-only dataframes.\n\n"
            "Hint: you probably called `nw.from_native` on an object which isn't fully "
            "supported by Narwhals, yet implements `__dataframe__`. If you would like to "
            "see this kind of object supported in Narwhals, please open a feature request "
            "at https://github.com/narwhals-dev/narwhals/issues."
        )
        raise NotImplementedError(msg)