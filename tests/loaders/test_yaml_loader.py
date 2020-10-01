import pytest
from prunner.loaders.yaml import YamlLoader, SectionNotDefined


def test_load_invalid_path():
    loader = YamlLoader()

    with pytest.raises(FileNotFoundError):
        loader.load("does_not_exist.yaml")


def test_load_valid_path():
    loader = YamlLoader()
    assert loader.load("tests/sample_files/test_file.yml") is not None


@pytest.fixture
def loader():
    return YamlLoader("tests/sample_files/test_file.yml")


def test_has_section_notexists(loader):
    result = loader.has_section("does_not_exist")
    assert result == False


def test_has_section_exists(loader):
    result = loader.has_section("dict_section")
    assert result == True


def test_get_section_returns_correct_section_type(loader):
    result = loader.get_section("dict_section")
    assert type(result) is dict

    result = loader.get_section("list_section")
    assert type(result) is list


def test_get_section_returns_error(loader):
    with pytest.raises(SectionNotDefined):
        loader.get_section("does_not_exist")
