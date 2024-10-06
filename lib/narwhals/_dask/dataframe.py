from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any
from typing import Iterable
from typing import Literal
from typing import Sequence

from narwhals._dask.utils import add_row_index
from narwhals._dask.utils import parse_exprs_and_named_exprs
from narwhals._pandas_like.utils import native_to_narwhals_dtype
from narwhals.utils import Implementation
from narwhals.utils import flatten
from narwhals.utils import generate_unique_token
from narwhals.utils import parse_columns_to_drop
from narwhals.utils import parse_version

if TYPE_CHECKING:
    from types import ModuleType

    import dask.dataframe as dd
    from typing_extensions import Self

    from narwhals._dask.expr import DaskExpr
    from narwhals._dask.group_by import DaskLazyGroupBy
    from narwhals._dask.namespace import DaskNamespace
    from narwhals._dask.typing import IntoDaskExpr
    from narwhals.dtypes import DType
    from narwhals.typing import DTypes


class DaskLazyFrame:
    def __init__(
        self,
        native_dataframe: dd.DataFrame,
        *,
        backend_version: tuple[int, ...],
        dtypes: DTypes,
    ) -> None:
        self._native_frame = native_dataframe
        self._backend_version = backend_version
        self._implementation = Implementation.DASK
        self._dtypes = dtypes

    def __native_namespace__(self: Self) -> ModuleType:
        if self._implementation is Implementation.DASK:
            return self._implementation.to_native_namespace()

        msg = f"Expected dask, got: {type(self._implementation)}"  # pragma: no cover
        raise AssertionError(msg)

    def __narwhals_namespace__(self) -> DaskNamespace:
        from narwhals._dask.namespace import DaskNamespace

        return DaskNamespace(backend_version=self._backend_version, dtypes=self._dtypes)

    def __narwhals_lazyframe__(self) -> Self:
        return self

    def _from_native_frame(self, df: Any) -> Self:
        return self.__class__(
            df, backend_version=self._backend_version, dtypes=self._dtypes
        )

    def with_columns(self, *exprs: DaskExpr, **named_exprs: DaskExpr) -> Self:
        df = self._native_frame
        new_series = parse_exprs_and_named_exprs(self, *exprs, **named_exprs)
        df = df.assign(**new_series)
        return self._from_native_frame(df)

    def collect(self) -> Any:
        import pandas as pd  # ignore-banned-import()

        from narwhals._pandas_like.dataframe import PandasLikeDataFrame

        result = self._native_frame.compute()
        return PandasLikeDataFrame(
            result,
            implementation=Implementation.PANDAS,
            backend_version=parse_version(pd.__version__),
            dtypes=self._dtypes,
        )

    @property
    def columns(self) -> list[str]:
        return self._native_frame.columns.tolist()  # type: ignore[no-any-return]

    def filter(
        self,
        *predicates: DaskExpr,
    ) -> Self:
        if (
            len(predicates) == 1
            and isinstance(predicates[0], list)
            and all(isinstance(x, bool) for x in predicates[0])
        ):
            msg = (
                "`LazyFrame.filter` is not supported for Dask backend with boolean masks."
            )
            raise NotImplementedError(msg)

        from narwhals._dask.namespace import DaskNamespace

        plx = DaskNamespace(backend_version=self._backend_version, dtypes=self._dtypes)
        expr = plx.all_horizontal(*predicates)
        # Safety: all_horizontal's expression only returns a single column.
        mask = expr._call(self)[0]
        return self._from_native_frame(self._native_frame.loc[mask])

    def select(
        self: Self,
        *exprs: IntoDaskExpr,
        **named_exprs: IntoDaskExpr,
    ) -> Self:
        import dask.dataframe as dd  # ignore-banned-import

        if exprs and all(isinstance(x, str) for x in exprs) and not named_exprs:
            # This is a simple slice => fastpath!
            return self._from_native_frame(self._native_frame.loc[:, exprs])

        new_series = parse_exprs_and_named_exprs(self, *exprs, **named_exprs)

        if not new_series:
            # return empty dataframe, like Polars does
            import pandas as pd  # ignore-banned-import

            return self._from_native_frame(
                dd.from_pandas(pd.DataFrame(), npartitions=self._native_frame.npartitions)
            )

        if all(getattr(expr, "_returns_scalar", False) for expr in exprs) and all(
            getattr(val, "_returns_scalar", False) for val in named_exprs.values()
        ):
            df = dd.concat(
                [val.to_series().rename(name) for name, val in new_series.items()], axis=1
            )
            return self._from_native_frame(df)

        df = self._native_frame.assign(**new_series).loc[:, list(new_series.keys())]
        return self._from_native_frame(df)

    def drop_nulls(self: Self, subset: str | list[str] | None) -> Self:
        if subset is None:
            return self._from_native_frame(self._native_frame.dropna())
        subset = [subset] if isinstance(subset, str) else subset
        plx = self.__narwhals_namespace__()
        return self.filter(~plx.any_horizontal(plx.col(*subset).is_null()))

    @property
    def schema(self) -> dict[str, DType]:
        return {
            col: native_to_narwhals_dtype(self._native_frame.loc[:, col], self._dtypes)
            for col in self._native_frame.columns
        }

    def collect_schema(self) -> dict[str, DType]:
        return self.schema

    def drop(self: Self, columns: list[str], strict: bool) -> Self:  # noqa: FBT001
        to_drop = parse_columns_to_drop(
            compliant_frame=self, columns=columns, strict=strict
        )

        return self._from_native_frame(self._native_frame.drop(columns=to_drop))

    def with_row_index(self: Self, name: str) -> Self:
        # Implementation is based on the following StackOverflow reply:
        # https://stackoverflow.com/questions/60831518/in-dask-how-does-one-add-a-range-of-integersauto-increment-to-a-new-column/60852409#60852409
        return self._from_native_frame(add_row_index(self._native_frame, name))

    def rename(self: Self, mapping: dict[str, str]) -> Self:
        return self._from_native_frame(self._native_frame.rename(columns=mapping))

    def head(self: Self, n: int) -> Self:
        return self._from_native_frame(
            self._native_frame.head(n=n, compute=False, npartitions=-1)
        )

    def unique(
        self: Self,
        subset: str | list[str] | None,
        *,
        keep: Literal["any", "first", "last", "none"] = "any",
        maintain_order: bool = False,
    ) -> Self:
        """
        NOTE:
            The param `maintain_order` is only here for compatibility with the polars API
            and has no effect on the output.
        """
        subset = flatten(subset) if subset else None
        native_frame = self._native_frame
        if keep == "none":
            subset = subset or self.columns
            token = generate_unique_token(n_bytes=8, columns=subset)
            ser = native_frame.groupby(subset).size().rename(token)
            ser = ser.loc[ser == 1]
            unique = ser.reset_index().drop(columns=token)
            result = native_frame.merge(unique, on=subset, how="inner")
        else:
            mapped_keep = {"any": "first"}.get(keep, keep)
            result = native_frame.drop_duplicates(subset=subset, keep=mapped_keep)
        return self._from_native_frame(result)

    def sort(
        self: Self,
        by: str | Iterable[str],
        *more_by: str,
        descending: bool | Sequence[bool],
        nulls_last: bool,
    ) -> Self:
        flat_keys = flatten([*flatten([by]), *more_by])
        df = self._native_frame
        if isinstance(descending, bool):
            ascending: bool | list[bool] = not descending
        else:
            ascending = [not d for d in descending]
        na_position = "last" if nulls_last else "first"
        return self._from_native_frame(
            df.sort_values(flat_keys, ascending=ascending, na_position=na_position)
        )

    def join(
        self: Self,
        other: Self,
        *,
        how: Literal["left", "inner", "outer", "cross", "anti", "semi"] = "inner",
        left_on: str | list[str] | None,
        right_on: str | list[str] | None,
        suffix: str,
    ) -> Self:
        if isinstance(left_on, str):
            left_on = [left_on]
        if isinstance(right_on, str):
            right_on = [right_on]
        if how == "cross":
            key_token = generate_unique_token(
                n_bytes=8, columns=[*self.columns, *other.columns]
            )

            return self._from_native_frame(
                self._native_frame.assign(**{key_token: 0})
                .merge(
                    other._native_frame.assign(**{key_token: 0}),
                    how="inner",
                    left_on=key_token,
                    right_on=key_token,
                    suffixes=("", suffix),
                )
                .drop(columns=key_token),
            )

        if how == "anti":
            indicator_token = generate_unique_token(
                n_bytes=8, columns=[*self.columns, *other.columns]
            )

            other_native = (
                other._native_frame.loc[:, right_on]
                .rename(  # rename to avoid creating extra columns in join
                    columns=dict(zip(right_on, left_on))  # type: ignore[arg-type]
                )
                .drop_duplicates()
            )
            df = self._native_frame.merge(
                other_native,
                how="outer",
                indicator=indicator_token,
                left_on=left_on,
                right_on=left_on,
            )
            return self._from_native_frame(
                df.loc[df[indicator_token] == "left_only"].drop(columns=[indicator_token])
            )

        if how == "semi":
            other_native = (
                other._native_frame.loc[:, right_on]
                .rename(  # rename to avoid creating extra columns in join
                    columns=dict(zip(right_on, left_on))  # type: ignore[arg-type]
                )
                .drop_duplicates()  # avoids potential rows duplication from inner join
            )
            return self._from_native_frame(
                self._native_frame.merge(
                    other_native,
                    how="inner",
                    left_on=left_on,
                    right_on=left_on,
                )
            )

        if how == "left":
            other_native = other._native_frame
            result_native = self._native_frame.merge(
                other_native,
                how="left",
                left_on=left_on,
                right_on=right_on,
                suffixes=("", suffix),
            )
            extra = []
            for left_key, right_key in zip(left_on, right_on):  # type: ignore[arg-type]
                if right_key != left_key and right_key not in self.columns:
                    extra.append(right_key)
                elif right_key != left_key:
                    extra.append(f"{right_key}_right")
            return self._from_native_frame(result_native.drop(columns=extra))

        return self._from_native_frame(
            self._native_frame.merge(
                other._native_frame,
                left_on=left_on,
                right_on=right_on,
                how=how,
                suffixes=("", suffix),
            ),
        )

    def join_asof(
        self,
        other: Self,
        *,
        left_on: str | None = None,
        right_on: str | None = None,
        on: str | None = None,
        by_left: str | list[str] | None = None,
        by_right: str | list[str] | None = None,
        by: str | list[str] | None = None,
        strategy: Literal["backward", "forward", "nearest"] = "backward",
    ) -> Self:
        plx = self.__native_namespace__()
        return self._from_native_frame(
            plx.merge_asof(
                self._native_frame,
                other._native_frame,
                left_on=left_on,
                right_on=right_on,
                on=on,
                left_by=by_left,
                right_by=by_right,
                by=by,
                direction=strategy,
                suffixes=("", "_right"),
            ),
        )

    def group_by(self, *by: str) -> DaskLazyGroupBy:
        from narwhals._dask.group_by import DaskLazyGroupBy

        return DaskLazyGroupBy(self, list(by))

    def tail(self: Self, n: int) -> Self:
        native_frame = self._native_frame
        n_partitions = native_frame.npartitions

        if n_partitions == 1:
            return self._from_native_frame(self._native_frame.tail(n=n, compute=False))
        else:
            msg = "`LazyFrame.tail` is not supported for Dask backend with multiple partitions."
            raise NotImplementedError(msg)

    def gather_every(self: Self, n: int, offset: int) -> Self:
        row_index_token = generate_unique_token(n_bytes=8, columns=self.columns)
        pln = self.__narwhals_namespace__()
        return (
            self.with_row_index(name=row_index_token)
            .filter(
                pln.col(row_index_token) >= offset,  # type: ignore[operator]
                (pln.col(row_index_token) - offset) % n == 0,  # type: ignore[arg-type]
            )
            .drop([row_index_token], strict=False)
        )

    def unpivot(
        self: Self,
        on: str | list[str] | None,
        index: str | list[str] | None,
        variable_name: str | None,
        value_name: str | None,
    ) -> Self:
        return self._from_native_frame(
            self._native_frame.melt(
                id_vars=index,
                value_vars=on,
                var_name=variable_name if variable_name is not None else "variable",
                value_name=value_name if value_name is not None else "value",
            )
        )