import closed_llm_platform


def test_package_exposes_version_alias():
    assert closed_llm_platform.version == "0.1.0"
    assert closed_llm_platform.__version__ == closed_llm_platform.version
