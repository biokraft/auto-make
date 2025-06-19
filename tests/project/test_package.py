"""Tests for package structure and imports."""

from importlib import import_module


class TestPackageStructure:
    """Test cases for package structure and imports."""

    def test_package_imports(self) -> None:
        """Test that the main package can be imported."""
        import automake

        assert automake is not None

    def test_version_attribute(self) -> None:
        """Test that version attribute is available."""
        import automake

        assert hasattr(automake, "__version__")
        assert isinstance(automake.__version__, str)
        assert len(automake.__version__) > 0

    def test_author_attribute(self) -> None:
        """Test that author attribute is available."""
        import automake

        assert hasattr(automake, "__author__")
        assert isinstance(automake.__author__, str)
        assert len(automake.__author__) > 0

    def test_email_attribute(self) -> None:
        """Test that email attribute is available."""
        import automake

        assert hasattr(automake, "__email__")
        assert isinstance(automake.__email__, str)
        assert "@" in automake.__email__

    def test_main_app_imports(self) -> None:
        """Test that main app can be imported."""
        from automake.cli import app

        assert app is not None

    def test_main_app_exists(self) -> None:
        """Test that the main app object exists."""
        from automake.cli.app import app

        assert app is not None

    def test_version_consistency(self) -> None:
        """Test that version is consistent across package and main."""
        import automake
        from automake import __version__

        assert automake.__version__ == __version__

    def test_all_exports(self) -> None:
        """Test that __all__ exports are valid."""
        import automake

        if hasattr(automake, "__all__"):
            for item in automake.__all__:
                assert hasattr(automake, item), f"Missing export: {item}"

    def test_module_docstring(self) -> None:
        """Test that modules have proper docstrings."""
        import importlib

        import automake

        app_module = importlib.import_module("automake.cli.app")

        assert automake.__doc__ is not None
        assert len(automake.__doc__.strip()) > 0
        assert app_module.__doc__ is not None
        assert len(app_module.__doc__.strip()) > 0

    def test_dynamic_import(self) -> None:
        """Test dynamic import of the package."""
        module = import_module("automake")
        assert module is not None
        assert hasattr(module, "__version__")

    def test_main_app_dynamic_import(self) -> None:
        """Test dynamic import of the main app module."""
        module = import_module("automake.cli.app")
        assert module is not None
        assert hasattr(module, "app")
        assert hasattr(module, "version_callback")
