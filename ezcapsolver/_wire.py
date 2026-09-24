"""Mapping between dataclasses and the service's wire format.

The service uses camelCase, with occasional irregular spellings such as
``websiteURL`` and ``script_base64``. Each field declares its wire name through
:func:`wire`, and every model shares one :meth:`Model.to_dict` /
:meth:`Model.from_dict` implementation.

There is deliberately no type validation here: Python is duck-typed, a missing
required field already fails in the dataclass constructor, and a hand-rolled
validator would only grow into half of pydantic with nobody maintaining it.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import MISSING, dataclass, field, fields
from typing import Any, ClassVar, Self

from .errors import SolutionDecodeError

__all__ = ["Model", "extra", "wire"]

_WIRE = "ezcapsolver.wire"
_OMIT_NONE = "ezcapsolver.omit_none"
_EXTRA = "ezcapsolver.extra"


def wire(
    name: str | None = None,
    *,
    default: Any = MISSING,
    default_factory: Any = MISSING,
    omit_none: bool = True,
) -> Any:
    """Declare a field together with its wire name.

    Args:
        name: Wire field name. Derived from the snake_case attribute name by
            converting it to camelCase when omitted.
        default: Default value.
        default_factory: Factory for mutable defaults.
        omit_none: Whether to drop the field from the request when its value
            is ``None``.

    Returns:
        A dataclass field carrying the mapping metadata.
    """
    metadata = {_WIRE: name, _OMIT_NONE: omit_none}
    if default_factory is not MISSING:
        return field(default_factory=default_factory, metadata=metadata)
    if default is not MISSING:
        return field(default=default, metadata=metadata)
    return field(metadata=metadata)


def extra() -> Any:
    """Declare the ``extra`` field that carries unmodelled fields.

    On the request side it is flattened into the payload; on the response side
    it catches every unknown key. This is where losslessness lands: a worker
    that adds a field does not lose it.
    """
    return field(default_factory=dict, metadata={_EXTRA: True})


def _camel(name: str) -> str:
    """Convert snake_case to camelCase."""
    head, *rest = name.split("_")
    return head + "".join(part.capitalize() for part in rest)


@dataclass(frozen=True, slots=True)
class _Spec:
    """Mapping rule for a single field."""

    name: str
    wire: str
    omit_none: bool
    is_extra: bool


def _unwrap(value: Any) -> Any:
    """Expand nested models into JSON-serialisable values."""
    if isinstance(value, Model):
        return value.to_dict()
    if isinstance(value, Mapping):
        return {k: _unwrap(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_unwrap(item) for item in value]
    return value


class Model:
    """Shared wire-format mapping. Subclasses must be dataclasses."""

    __slots__ = ()

    #: Each subclass caches its own field rules.
    _wire_specs_cache: ClassVar[tuple[_Spec, ...] | None] = None

    @classmethod
    def _specs(cls) -> tuple[_Spec, ...]:
        """Return this class's field mapping rules, cached per class."""
        cached = cls.__dict__.get("_wire_specs_cache")
        if cached is not None:
            return cached  # type: ignore[no-any-return]
        specs = tuple(
            _Spec(
                name=f.name,
                wire=f.metadata.get(_WIRE) or _camel(f.name),
                omit_none=bool(f.metadata.get(_OMIT_NONE, True)),
                is_extra=bool(f.metadata.get(_EXTRA, False)),
            )
            for f in fields(cls)  # type: ignore[arg-type]
        )
        cls._wire_specs_cache = specs
        return specs

    def to_dict(self) -> dict[str, Any]:
        """Serialise into the dictionary the service expects."""
        specs = self._specs()
        payload = {
            spec.wire: _unwrap(getattr(self, spec.name))
            for spec in specs
            if not spec.is_extra and not (getattr(self, spec.name) is None and spec.omit_none)
        }
        # Merge extra last without overwriting modelled fields: an accidental duplicate
        # in pass-through data must not silently replace an explicit parameter.
        for spec in specs:
            if spec.is_extra:
                for key, value in (getattr(self, spec.name) or {}).items():
                    payload.setdefault(key, _unwrap(value))
        return payload

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Self:
        """Decode from a wire dictionary, collecting unknown keys into ``extra``.

        Raises:
            SolutionDecodeError: The data is not an object, or a required field
                is missing. The raw value travels with the error, since that is
                exactly what diagnosing the failure needs.
        """
        if not isinstance(data, Mapping):
            raise SolutionDecodeError(
                raw=data, cause=TypeError(f"expected an object, got {type(data).__name__}")
            )

        specs = cls._specs()
        known = {spec.wire for spec in specs if not spec.is_extra}
        kwargs = {
            spec.name: data[spec.wire] for spec in specs if not spec.is_extra and spec.wire in data
        }
        for spec in specs:
            if spec.is_extra:
                kwargs[spec.name] = {k: v for k, v in data.items() if k not in known}

        try:
            return cls(**kwargs)
        except TypeError as exc:
            raise SolutionDecodeError(raw=dict(data), cause=exc) from exc
