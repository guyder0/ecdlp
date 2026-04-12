import pytest
import pathlib
from ecdlp.utils.ecgen_loader import ECGenLoader

def get_dataset_paths():
    base_path = pathlib.Path(__file__).parent.parent / "curves" / "dataset"
    return {
        "anomalous": list((base_path / "anomalous").glob("*.json")),
        "smooth": list((base_path / "smooth").glob("*.json")),
        "general": list((base_path / "general").glob("*.json")),
    }

def pytest_generate_tests(metafunc):
    """Динамически создает тесты на основе файлов в датасете."""
    paths = get_dataset_paths()
    
    if "case_anomalous" in metafunc.fixturenames:
        cases = []
        for p in paths["anomalous"]:
            cases.extend(ECGenLoader.load_from_json_file(str(p)))
        metafunc.parametrize("case_anomalous", cases)

    if "case_smooth" in metafunc.fixturenames:
        cases = []
        for p in paths["smooth"]:
            cases.extend(ECGenLoader.load_from_json_file(str(p)))
        metafunc.parametrize("case_smooth", cases)

    if "case_general" in metafunc.fixturenames:
        cases = []
        for p in paths["general"]:
            cases.extend(ECGenLoader.load_from_json_file(str(p)))
        metafunc.parametrize("case_general", cases)