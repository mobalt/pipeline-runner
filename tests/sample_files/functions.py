print(
    "__file__={0:<35} | __name__={1:<20} | __package__={2:<20}".format(
        __file__, __name__, str(__package__)
    )
)

from .secondary import second_function


def example_function():
    pass


def call_secondary():
    return second_function()
