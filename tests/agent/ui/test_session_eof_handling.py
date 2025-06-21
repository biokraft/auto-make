"""Tests for interactive session EOF handling."""

from unittest.mock import MagicMock, patch

from automake.agent.ui.session import RichInteractiveSession


class TestSessionEOFHandling:
    """Test cases for EOF handling in interactive sessions."""

    def test_eof_handling_in_start_method(self):
        """Test that EOFError is handled gracefully in start method."""
        mock_agent = MagicMock()
        session = RichInteractiveSession(mock_agent)

        # Mock get_user_input to raise EOFError (Ctrl+D)
        with patch.object(session, "get_user_input", side_effect=EOFError):
            # Should not raise exception, should exit gracefully
            session.start()

    def test_eof_shows_goodbye_message(self):
        """Test that EOF handling shows a goodbye message."""
        mock_agent = MagicMock()
        session = RichInteractiveSession(mock_agent)

        with (
            patch.object(session, "get_user_input", side_effect=EOFError),
            patch.object(session.console, "print") as mock_print,
        ):
            session.start()

            # Should have printed a goodbye message
            print_calls = [call.args[0] for call in mock_print.call_args_list]
            goodbye_messages = [
                msg for msg in print_calls if "goodbye" in msg.lower() or "👋" in msg
            ]
            assert len(goodbye_messages) > 0

    def test_eof_cleans_up_live_ui_components(self):
        """Test that EOF handling cleans up live UI components."""
        mock_agent = MagicMock()
        session = RichInteractiveSession(mock_agent)

        # Mock a live component
        mock_live = MagicMock()
        session._live = mock_live

        with patch.object(session, "get_user_input", side_effect=EOFError):
            session.start()

            # Live component should be cleaned up (stopped)
            mock_live.stop.assert_called()

    def test_keyboard_interrupt_handling(self):
        """Test that KeyboardInterrupt is handled gracefully."""
        mock_agent = MagicMock()
        session = RichInteractiveSession(mock_agent)

        with (
            patch.object(session, "get_user_input", side_effect=KeyboardInterrupt),
            patch.object(session.console, "print") as mock_print,
        ):
            session.start()

            # Should have printed an interrupted message
            print_calls = [call.args[0] for call in mock_print.call_args_list]
            interrupt_messages = [
                msg for msg in print_calls if "interrupt" in msg.lower() or "👋" in msg
            ]
            assert len(interrupt_messages) > 0

    def test_graceful_session_termination_on_eof(self):
        """Test that session terminates gracefully on EOF."""
        mock_agent = MagicMock()
        session = RichInteractiveSession(mock_agent)

        def mock_start():
            try:
                session.start()
            except SystemExit:
                pass  # Expected for graceful exit

        with patch.object(session, "get_user_input", side_effect=EOFError):
            mock_start()

        # Session should have completed without unhandled exceptions
        # (session_completed might be False if it exits via sys.exit, which is fine)

    def test_eof_does_not_show_error_message(self):
        """Test that EOF doesn't show error messages, just graceful exit."""
        mock_agent = MagicMock()
        session = RichInteractiveSession(mock_agent)

        with (
            patch.object(session, "get_user_input", side_effect=EOFError),
            patch.object(session.console, "print") as mock_print,
        ):
            session.start()

            # Should not have printed any error messages
            print_calls = [call.args[0] for call in mock_print.call_args_list]
            error_messages = [
                msg for msg in print_calls if "error" in msg.lower() or "❌" in msg
            ]
            assert len(error_messages) == 0

    def test_session_cleanup_on_eof(self):
        """Test that session performs cleanup on EOF."""
        mock_agent = MagicMock()
        session = RichInteractiveSession(mock_agent)

        # Add a cleanup function to track
        cleanup_called = False

        def cleanup_func():
            nonlocal cleanup_called
            cleanup_called = True

        session._cleanup_functions = [cleanup_func]

        with patch.object(session, "get_user_input", side_effect=EOFError):
            session.start()

        # Cleanup should have been called
        assert cleanup_called

    def test_eof_handling_with_signal_handler_integration(self):
        """Test that EOF handling integrates properly with signal handler."""
        mock_agent = MagicMock()

        with patch(
            "automake.core.signal_handler.SignalHandler.get_instance"
        ) as mock_get_handler:
            mock_handler = MagicMock()
            mock_get_handler.return_value = mock_handler

            # Create session after setting up the mock
            session = RichInteractiveSession(mock_agent)

            with patch.object(session, "get_user_input", side_effect=EOFError):
                session.start()

            # Should have registered cleanup with signal handler
            mock_handler.register_cleanup.assert_called()

    def test_multiple_eof_handling(self):
        """Test that multiple EOF signals are handled gracefully."""
        mock_agent = MagicMock()
        session = RichInteractiveSession(mock_agent)

        # Simulate EOF on first input attempt
        eof_count = 0

        def raise_eof():
            nonlocal eof_count
            eof_count += 1
            raise EOFError()  # Always raise EOF - should terminate immediately

        with patch.object(session, "get_user_input", side_effect=raise_eof):
            session.start()

        # Should have called get_user_input at least once and handled EOF gracefully
        # EOF should terminate immediately, so only one call expected
        assert eof_count == 1
