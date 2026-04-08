import wikiops_sdk
import wikiops_sdk.compat as compat
import wikiops_sdk.contracts as contracts
import wikiops_sdk.domain as domain


def test_top_level_exports_match_module_attributes() -> None:
    for name in wikiops_sdk.__all__:
        assert hasattr(wikiops_sdk, name)


def test_contracts_exports_match_module_attributes() -> None:
    for name in contracts.__all__:
        assert hasattr(contracts, name)


def test_domain_exports_match_module_attributes() -> None:
    for name in domain.__all__:
        assert hasattr(domain, name)


def test_compat_exports_match_module_attributes() -> None:
    for name in compat.__all__:
        assert hasattr(compat, name)
