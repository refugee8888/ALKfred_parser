import src.utils



def test_normalize_label_handles_double_colon():
   
    
    out = src.utils.normalize_label("ALK::fusion")
    assert out == "alk_fusion"


