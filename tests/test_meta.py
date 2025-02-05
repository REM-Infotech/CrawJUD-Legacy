"""
Unit tests for the PropertiesCrawJUD class from the bot.shared module.

The tests are written using the pytest framework and cover various properties and methods of the PropertiesCrawJUD class.

Fixtures:
    setup_PropertiesCrawJUD: A pytest fixture that returns an instance of the PropertiesCrawJUD class.

Tests:
    test_appends: Tests the 'appends' property.
    test_another_append: Tests the 'another_append' property.
    test_OpenAI_client: Tests the 'OpenAI_client' property.
    test_system: Tests the 'system' property.
    test_state_or_client: Tests the 'state_or_client' property.
    test_type_log: Tests the 'type_log' property.
    test_pid: Tests the 'pid' property.
    test_message: Tests the 'message' property.
    test_isStoped: Tests the 'isStoped' property by mocking the os.path.exists function.
    test_chr_dir: Tests the 'chr_dir' property.
    test_output_dir_path: Tests the 'output_dir_path' property.
    test_kwrgs: Tests the 'kwrgs' property.
    test_row: Tests the 'row' property.
    test_message_error: Tests the 'message_error' property.
    test_graphicMode: Tests the 'graphicMode' property.
    test_bot_data: Tests the 'bot_data' property.
    test_vara: Tests the 'vara' property.
    test_path_accepted: Tests the 'path_accepted' property.
"""

import pytest

from bot.shared import PropertiesCrawJUD


@pytest.fixture
def setup_PropertiesCrawJUD():
    """Return an instance of the PropertiesCrawJUD class."""
    return PropertiesCrawJUD()


def test_appends(setup_PropertiesCrawJUD):
    """Test the 'appends' property."""
    setup_PropertiesCrawJUD.appends = ["test"]
    assert setup_PropertiesCrawJUD.appends == ["test"]  # nosec B101


def test_another_append(setup_PropertiesCrawJUD):
    """Test the 'another_append' property."""
    setup_PropertiesCrawJUD.another_append = ["another_test"]
    assert setup_PropertiesCrawJUD.another_append == ["another_test"]  # nosec B101


def test_OpenAI_client(setup_PropertiesCrawJUD):
    """Test the 'OpenAI_client' property."""
    assert setup_PropertiesCrawJUD.OpenAI_client is not None  # nosec B101


def test_system(setup_PropertiesCrawJUD):
    """Test the 'system' property."""
    setup_PropertiesCrawJUD.system = "test_system"
    assert setup_PropertiesCrawJUD.system == "test_system"  # nosec B101


def test_state_or_client(setup_PropertiesCrawJUD):
    """Test the 'state_or_client' property."""
    setup_PropertiesCrawJUD.state_or_client = "test_client"
    assert setup_PropertiesCrawJUD.state_or_client == "test_client"  # nosec B101


def test_type_log(setup_PropertiesCrawJUD):
    """Test the 'type_log' property."""
    setup_PropertiesCrawJUD.type_log = "error"
    assert setup_PropertiesCrawJUD.type_log == "error"  # nosec B101


def test_pid(setup_PropertiesCrawJUD):
    """Test the 'pid' property."""
    setup_PropertiesCrawJUD.pid = "12345"
    assert setup_PropertiesCrawJUD.pid == "12345"  # nosec B101


def test_message(setup_PropertiesCrawJUD):
    """Test the 'message' property."""
    setup_PropertiesCrawJUD.message = "test_message"
    assert setup_PropertiesCrawJUD.message == "test_message"  # nosec B101


def test_isStoped(setup_PropertiesCrawJUD, mocker):
    """Test the 'isStoped' property by mocking the os.path.exists function."""
    mocker.patch("os.path.exists", return_value=True)
    assert setup_PropertiesCrawJUD.isStoped is True  # nosec B101


def test_chr_dir(setup_PropertiesCrawJUD):
    """Test the 'chr_dir' property."""
    setup_PropertiesCrawJUD.chr_dir = "test_dir"
    assert setup_PropertiesCrawJUD.chr_dir == "test_dir"  # nosec B101


def test_output_dir_path(setup_PropertiesCrawJUD):
    """Test the 'output_dir_path' property."""
    setup_PropertiesCrawJUD.output_dir_path = "output_dir"
    assert setup_PropertiesCrawJUD.output_dir_path == "output_dir"  # nosec B101


def test_kwrgs(setup_PropertiesCrawJUD):
    """Test the 'kwrgs' property."""
    setup_PropertiesCrawJUD.kwrgs = {"key": "value"}
    assert setup_PropertiesCrawJUD.kwrgs == {"key": "value"}  # nosec B101


def test_row(setup_PropertiesCrawJUD):
    """Test the 'row' property."""
    setup_PropertiesCrawJUD.row = 1
    assert setup_PropertiesCrawJUD.row == 1  # nosec B101


def test_message_error(setup_PropertiesCrawJUD):
    """Test the 'message_error' property."""
    setup_PropertiesCrawJUD.message_error = "error_message"
    assert setup_PropertiesCrawJUD.message_error == "error_message"  # nosec B101


def test_graphicMode(setup_PropertiesCrawJUD):
    """Test the 'graphicMode' property."""
    setup_PropertiesCrawJUD.graphicMode = "bar"
    assert setup_PropertiesCrawJUD.graphicMode == "bar"  # nosec B101


def test_bot_data(setup_PropertiesCrawJUD):
    """Test the 'bot_data' property."""
    setup_PropertiesCrawJUD.bot_data = {"bot_key": "bot_value"}
    assert setup_PropertiesCrawJUD.bot_data == {"bot_key": "bot_value"}  # nosec B101


def test_vara(setup_PropertiesCrawJUD):
    """Test the 'vara' property."""
    setup_PropertiesCrawJUD.vara = "test_vara"
    assert setup_PropertiesCrawJUD.vara == "test_vara"  # nosec B101


def test_path_accepted(setup_PropertiesCrawJUD):
    """Test the 'path_accepted' property."""
    setup_PropertiesCrawJUD.path_accepted = "test_path"
    assert setup_PropertiesCrawJUD.path_accepted == "test_path"  # nosec B101
