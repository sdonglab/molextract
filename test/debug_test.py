from unittest import mock
import pytest

from molextract import debug


@mock.patch('sys.stderr.isatty', return_value=True)
def test_color(mock_isatty):
    for color in debug._COLOR_CODES:
        code = debug._COLOR_CODES[color]
        string = f'{debug.ESC_CHAR}{code}m'
        assert debug.Color.__getattr__(color) == string

    with pytest.raises(ValueError, match='not a valid color'):
        debug.Color.ORANGE


@mock.patch('sys.stderr.isatty')
def test_color_notty(mock_isatty):
    mock_isatty.return_value = True
    assert len(debug.Color.RED) > 0

    mock_isatty.return_value = False
    assert debug.Color.RED == ''
