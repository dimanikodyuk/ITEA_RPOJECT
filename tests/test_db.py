import pytest

# проверка наличия файла БД
@pytest.mark.parametrize("file_path", [("../project/crm.db")])
def test_file_exist(file_path):
    assert open(file_path)
