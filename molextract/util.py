import molextract
import pathlib

MOLEXTRACT_MODULE_DIR = pathlib.Path(molextract.__file__).parent
TEST_FILE_DIR = MOLEXTRACT_MODULE_DIR.parent / 'test_files'

def molextract_test_file(name) -> pathlib.Path:
    path = TEST_FILE_DIR / name
    assert path.exists(), f"test file '{name}' does not exist"
    return path


