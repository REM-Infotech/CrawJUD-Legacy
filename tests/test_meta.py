"""
This module contains unit tests for the PropertiesCrawJUD class from the bot.shared module.

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
    return PropertiesCrawJUD()


def test_appends(setup_PropertiesCrawJUD):
    setup_PropertiesCrawJUD.appends = ["test"]
    assert setup_PropertiesCrawJUD.appends == ["test"]


def test_another_append(setup_PropertiesCrawJUD):
    setup_PropertiesCrawJUD.another_append = ["another_test"]
    assert setup_PropertiesCrawJUD.another_append == ["another_test"]


def test_OpenAI_client(setup_PropertiesCrawJUD):
    assert setup_PropertiesCrawJUD.OpenAI_client is not None


def test_system(setup_PropertiesCrawJUD):
    setup_PropertiesCrawJUD.system = "test_system"
    assert setup_PropertiesCrawJUD.system == "test_system"


def test_state_or_client(setup_PropertiesCrawJUD):
    setup_PropertiesCrawJUD.state_or_client = "test_client"
    assert setup_PropertiesCrawJUD.state_or_client == "test_client"


def test_type_log(setup_PropertiesCrawJUD):
    setup_PropertiesCrawJUD.type_log = "error"
    assert setup_PropertiesCrawJUD.type_log == "error"


def test_pid(setup_PropertiesCrawJUD):
    setup_PropertiesCrawJUD.pid = "12345"
    assert setup_PropertiesCrawJUD.pid == "12345"


def test_message(setup_PropertiesCrawJUD):
    setup_PropertiesCrawJUD.message = "test_message"
    assert setup_PropertiesCrawJUD.message == "test_message"


def test_isStoped(setup_PropertiesCrawJUD, mocker):
    """Test if the isStoped property correctly checks for the existence of the stop flag file."""
    mocker.patch("os.path.exists", return_value=True)
    assert setup_PropertiesCrawJUD.isStoped is True


def test_chr_dir(setup_PropertiesCrawJUD):
    setup_PropertiesCrawJUD.chr_dir = "test_dir"
    assert setup_PropertiesCrawJUD.chr_dir == "test_dir"


def test_output_dir_path(setup_PropertiesCrawJUD):
    setup_PropertiesCrawJUD.output_dir_path = "output_dir"
    assert setup_PropertiesCrawJUD.output_dir_path == "output_dir"


def test_kwrgs(setup_PropertiesCrawJUD):
    setup_PropertiesCrawJUD.kwrgs = {"key": "value"}
    assert setup_PropertiesCrawJUD.kwrgs == {"key": "value"}


def test_row(setup_PropertiesCrawJUD):
    setup_PropertiesCrawJUD.row = 1
    assert setup_PropertiesCrawJUD.row == 1


def test_message_error(setup_PropertiesCrawJUD):
    setup_PropertiesCrawJUD.message_error = "error_message"
    assert setup_PropertiesCrawJUD.message_error == "error_message"


def test_graphicMode(setup_PropertiesCrawJUD):
    setup_PropertiesCrawJUD.graphicMode = "bar"
    assert setup_PropertiesCrawJUD.graphicMode == "bar"


def test_bot_data(setup_PropertiesCrawJUD):
    setup_PropertiesCrawJUD.bot_data = {"bot_key": "bot_value"}
    assert setup_PropertiesCrawJUD.bot_data == {"bot_key": "bot_value"}


def test_vara(setup_PropertiesCrawJUD):
    setup_PropertiesCrawJUD.vara = "test_vara"
    assert setup_PropertiesCrawJUD.vara == "test_vara"


def test_path_accepted(setup_PropertiesCrawJUD):
    setup_PropertiesCrawJUD.path_accepted = "test_path"
    assert setup_PropertiesCrawJUD.path_accepted == "test_path"
