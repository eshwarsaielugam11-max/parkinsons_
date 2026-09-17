import pytest
from rag.ingestion.verify_sources import verify_source, is_approved

def test_verify_source_rejects_unapproved():
    unapproved_id = "random_source"
    # Should not be approved
    assert not is_approved(unapproved_id)
    with pytest.raises(ValueError) as exc:
        verify_source(unapproved_id)
    assert f"Source '{unapproved_id}' is not in the approved list" in str(exc.value)
