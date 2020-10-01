from prunner.util.convert import split_file_component


def test_split_file_component():
    assert split_file_component("Just content") == (None, "Just content")
    assert split_file_component("Filename#Content") == ("Filename", "Content")
