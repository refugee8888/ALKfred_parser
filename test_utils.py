import string
from _pytest import monkeypatch
import os
from _pytest.fixtures import FixtureRequest
import src.utils



def test_normalize_label_handles_double_colon():
   
    
    out = src.utils.normalize_label("ALK::fusion")
    assert out == "alk_fusion"


