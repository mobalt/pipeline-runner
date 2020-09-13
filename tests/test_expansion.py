from prunner.util import shellexpansion_dict, shellexpansion, VariableNotSet
from os.path import expanduser
import pytest


def test_tilde_expansion():
    result = shellexpansion("~/a/b/c", {})
    expected = expanduser("~") + "/a/b/c"
    assert result == expected


def test_single_variable():
    variables = {"FOO": "bar"}
    result = shellexpansion("$FOO", variables)
    expected = "bar"
    assert result == expected


def test_curly_variable():
    variables = {"FOO": "bar"}
    result = shellexpansion("${FOO}", variables)
    expected = "bar"
    assert result == expected


def test_curly_defaulted_variable():
    variables = {"FOO": "bar"}
    result = shellexpansion("${FOO}_${NOPE:yes}", variables)
    expected = "bar_yes"
    assert result == expected


def test_full_expansion():
    variables = {"A": "AA", "B": "BBB"}
    result = shellexpansion("~/$A/${B}/${C:C}", variables)
    home = expanduser("~")
    expected = f"{home}/AA/BBB/C"
    assert result == expected


def test_missing_variable_throws_exception():
    with pytest.raises(VariableNotSet):
        shellexpansion("$NotSet", {})


def test_shellexpansion_dict():
    test_input = {"static": "This should not change.", "dynamic": "${A}_$B"}
    variables = {"A": "AA", "B": "BBB"}
    result = shellexpansion_dict(test_input, variables)
    expected = {"static": "This should not change.", "dynamic": "AA_BBB"}
    assert result == expected
