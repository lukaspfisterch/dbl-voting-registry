import pytest

from dbl_ingress.admission.errors import InvalidInputError
from dbl_ingress.shaping.shape import shape_input


def test_ingress_rejects_float():
    with pytest.raises(InvalidInputError):
        shape_input(correlation_id="c", deterministic={"x": 0.1})


def test_ingress_rejects_set():
    with pytest.raises(InvalidInputError):
        shape_input(correlation_id="c", deterministic={"x": {"a"}})


def test_ingress_rejects_tuple():
    with pytest.raises(InvalidInputError):
        shape_input(correlation_id="c", deterministic={"x": ("a",)})


def test_ingress_rejects_custom_object():
    class X:
        pass

    with pytest.raises(InvalidInputError):
        shape_input(correlation_id="c", deterministic={"x": X()})


def test_ingress_deep_immutability():
    record = shape_input(correlation_id="c", deterministic={"x": {"y": 1}})
    with pytest.raises(TypeError):
        record.deterministic["x"]["y"] = 2  # type: ignore[index]
