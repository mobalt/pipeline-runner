import pytest
from prunner.loaders.template_loader import TemplateLoader
from jinja2 import TemplateNotFound, Template


@pytest.fixture
def loader():
    return TemplateLoader("example/templates")


def test_has_template_notexists(loader):
    result = loader.has_template("does_not_exist.jinja2")
    assert result == False


def test_has_template_exists(loader):
    result = loader.has_template("script.jinja2")
    assert result == True


def test_get_template_returns_template_type(loader):
    result = loader.get_template("script.jinja2")
    assert isinstance(result, Template)


def test_get_function_returns_error(loader):
    with pytest.raises(TemplateNotFound):
        result = loader.get_template("does_not_exist.jinja2")
