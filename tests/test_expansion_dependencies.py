import os
import pytest
from prunner.util.expand import shellexpand_dependencies as deps


def test_tilde():
    result = deps("~")
    assert result == {"HOME"}

    result2 = deps("~/blah")
    assert result2 == {"HOME"}


def test_complex_item():
    sample_list = ["$HOME/${FOO}", "${BAR:baz}"]
    sample_dict = {"list": sample_list, "unique": "$FROM_DICT"}
    sample_complex_list = ["$STRING", sample_dict]
    actual = deps(sample_complex_list)
    expected = {"HOME", "STRING", "FOO", "BAR", "FROM_DICT"}
    assert actual == expected
