import pytest

from bot.meta import classproperty


@pytest.fixture
def setup_classproperty():
    return classproperty()


def test_appends(setup_classproperty):
    setup_classproperty.appends = ["test"]
    assert setup_classproperty.appends == ["test"]


def test_another_append(setup_classproperty):
    setup_classproperty.another_append = ["another_test"]
    assert setup_classproperty.another_append == ["another_test"]


def test_OpenAI_client(setup_classproperty):
    assert setup_classproperty.OpenAI_client is not None


def test_system(setup_classproperty):
    setup_classproperty.system = "test_system"
    assert setup_classproperty.system == "test_system"


def test_state_or_client(setup_classproperty):
    setup_classproperty.state_or_client = "test_client"
    assert setup_classproperty.state_or_client == "test_client"


def test_type_log(setup_classproperty):
    setup_classproperty.type_log = "error"
    assert setup_classproperty.type_log == "error"


def test_pid(setup_classproperty):
    setup_classproperty.pid = "12345"
    assert setup_classproperty.pid == "12345"


def test_message(setup_classproperty):
    setup_classproperty.message = "test_message"
    assert setup_classproperty.message == "test_message"


def test_isStoped(setup_classproperty, mocker):
    """Test if the isStoped property correctly checks for the existence of the stop flag file."""
    mocker.patch("os.path.exists", return_value=True)
    assert setup_classproperty.isStoped is True


def test_chr_dir(setup_classproperty):
    setup_classproperty.chr_dir = "test_dir"
    assert setup_classproperty.chr_dir == "test_dir"


def test_output_dir_path(setup_classproperty):
    setup_classproperty.output_dir_path = "output_dir"
    assert setup_classproperty.output_dir_path == "output_dir"


def test_kwrgs(setup_classproperty):
    setup_classproperty.kwrgs = {"key": "value"}
    assert setup_classproperty.kwrgs == {"key": "value"}


def test_row(setup_classproperty):
    setup_classproperty.row = 1
    assert setup_classproperty.row == 1


def test_message_error(setup_classproperty):
    setup_classproperty.message_error = "error_message"
    assert setup_classproperty.message_error == "error_message"


def test_graphicMode(setup_classproperty):
    setup_classproperty.graphicMode = "bar"
    assert setup_classproperty.graphicMode == "bar"


def test_bot_data(setup_classproperty):
    setup_classproperty.bot_data = {"bot_key": "bot_value"}
    assert setup_classproperty.bot_data == {"bot_key": "bot_value"}


def test_vara(setup_classproperty):
    setup_classproperty.vara = "test_vara"
    assert setup_classproperty.vara == "test_vara"


def test_path_accepted(setup_classproperty):
    setup_classproperty.path_accepted = "test_path"
    assert setup_classproperty.path_accepted == "test_path"
