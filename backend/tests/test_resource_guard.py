"""
Unit tests for resource_guard: is_under_load, throttle_if_needed.
"""
import pytest
from backend.services.resource_guard import is_under_load, throttle_if_needed, _cached_sample


def test_is_under_load_returns_bool():
    assert isinstance(is_under_load(), bool)


def test_throttle_if_needed_no_raise():
    throttle_if_needed()


def test_cached_sample_returns_tuple():
    cpu, mem = _cached_sample()
    assert isinstance(cpu, (int, float))
    assert isinstance(mem, (int, float))
    assert mem >= 0
