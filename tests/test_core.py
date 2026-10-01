import pytest
from vec_p3_freeze.core import freeze, verify, checklist


def test_freeze_verify_and_two_slot_rule(tmp_path):
    src=tmp_path/'pred.h5ad'; src.write_bytes(b'prediction')
    bundle=tmp_path/'bundle'
    m=freeze(bundle,'T1:val',1,src,'best')
    assert len(m['sha256'])==64
    assert verify(bundle)[0]['status']=='OK'
    with pytest.raises(FileExistsError): freeze(bundle,'T1:val',1,src)
    with pytest.raises(ValueError): freeze(bundle,'T1:val',3,src)
    assert 'T1:val' in checklist(bundle)


def test_change_detected_even_if_readonly_bit_reset(tmp_path):
    src=tmp_path/'pred.h5ad'; src.write_bytes(b'a')
    bundle=tmp_path/'b'; m=freeze(bundle,'T3:gata4',2,src)
    frozen=bundle/m['file']; frozen.chmod(0o644); frozen.write_bytes(b'b')
    assert verify(bundle)[0]['status']=='CHANGED'
