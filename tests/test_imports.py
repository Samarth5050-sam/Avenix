# Tests for package imports and public API

import pytest


class TestPackageImports:
    """Verify that the public API is correctly exported."""

    def test_import_trace(self):
        """Test that 'from avenix import trace' succeeds."""
        from avenix import trace
        assert callable(trace)

    def test_import_tracer(self):
        """Test that 'from avenix import Tracer' succeeds."""
        from avenix import Tracer
        assert Tracer is not None

    def test_version_attribute(self):
        """Verify __version__ is accessible and equals '0.1.0'."""
        import avenix
        assert hasattr(avenix, '__version__')
        assert avenix.__version__ == '0.1.0'

    def test_all_contains_expected(self):
        """Verify __all__ contains only ['trace', 'Tracer']."""
        import avenix
        assert hasattr(avenix, '__all__')
        assert sorted(avenix.__all__) == sorted(['trace', 'Tracer'])

    def test_internal_modules_not_in_all(self):
        """Verify internal modules are not exposed in __all__."""
        import avenix
        internal_modules = ['formatter', 'logger', 'models', 'extractors']
        for module_name in internal_modules:
            assert module_name not in avenix.__all__, (
                f"Internal module '{module_name}' should not be in __all__"
            )
