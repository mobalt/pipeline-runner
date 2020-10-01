import types
import pytest
from prunner.loaders.function import FunctionLoader, FunctionNotDefined


def test_load_invalid_path():
    loader = FunctionLoader()
    with pytest.raises(FileNotFoundError):
        loader.load("does_not_exist.py")


def test_load_valid_path():
    loader = FunctionLoader()
    assert loader.load("tests/sample_files/functions.py") is not None


@pytest.fixture
def loader():
    return FunctionLoader("tests/sample_files/functions.py")


def test_has_function_notexists(loader):
    result = loader.has_function("does_not_exist")
    assert result == False


def test_has_function_exists(loader):
    result = loader.has_function("example_function")
    assert result == True


def test_get_function_returns_function_type(loader):
    result = loader.get_function("example_function")
    assert callable(result)
    assert type(result) == types.FunctionType


def test_get_function_returns_error(loader):
    with pytest.raises(FunctionNotDefined):
        loader.get_function("does_not_exist")
