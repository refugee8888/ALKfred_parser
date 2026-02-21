from civic_parser import gene_in_molecular_profile                                                                                                                                                                                                                                                                          
                                                                                                                                                                                                                                                                                                                              
                  


def test_simple_match():
    assert gene_in_molecular_profile("ALK L1196M", "ALK") is True

def test_simple_no_match():
    assert gene_in_molecular_profile("EGFR L858R", "ALK") is False


# Regex cases

def test_fusion_double_colon_match():
    # EML4::ALK
    assert gene_in_molecular_profile("EML4::ALK", "ALK") is True

def test_fusion_double_colon_no_partial():
    
    assert gene_in_molecular_profile("TALK1::EML4", "ALK") is False

def test_case_insensitive():
    assert gene_in_molecular_profile("alk l1196m", "ALK") is True

def test_gene_symbol_lowercased():
    assert gene_in_molecular_profile("ALK L1196M", "alk") is True


# Edge cases

def test_empty_mp_name_returns_false():
    assert gene_in_molecular_profile("", "ALK") is False

def test_none_mp_name_returns_false():
    assert gene_in_molecular_profile(None, "ALK") is False

def test_none_gene_symbol_returns_false():
    assert gene_in_molecular_profile("ALK L1196M", None) is False

def test_both_none_returns_false():
    assert gene_in_molecular_profile(None, None) is False