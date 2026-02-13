from importlib.metadata import version


def test_supported_stack_versions() -> None:
    assert version("pybotx").startswith("0.76.")
    assert version("pybotx-smartapp-rpc").startswith("0.13.")
