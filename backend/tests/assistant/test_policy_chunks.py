import pytest

from music_store.assistant.policy_chunks import load_policy_chunks
from music_store.settings import REPO_ROOT

PDF = REPO_ROOT / "data" / "store-policies.pdf"


@pytest.fixture(scope="module")
def chunks():
    return load_policy_chunks(PDF)


def _by_section(chunks):
    return {c.section: c for c in chunks}


def test_one_chunk_per_subsection_with_section_numbers(chunks):
    sections = _by_section(chunks)
    for number in ["1.2", "2", "3", "3.1", "4.1", "4.2", "4.3", "4.4", "5.1", "5.2", "5.3", "8.1"]:
        assert number in sections
    assert len(sections) == len(chunks)


def test_numbered_list_items_are_not_sections(chunks):
    sections = _by_section(chunks)
    assert "7.2" in sections
    assert "Saudação" in sections["7.2"].text
    assert "Entendimento" in sections["7.2"].text
    assert sections["2"].title == "Horário de Funcionamento"


def test_chunk_content_prepends_parent_section_title(chunks):
    chunk = _by_section(chunks)["4.1"]
    assert chunk.parent_title == "Política de Trocas e Devoluções"
    assert chunk.title.startswith("Direito de Arrependimento")
    assert chunk.content.startswith(
        "Política de Trocas e Devoluções\n4.1 Direito de Arrependimento"
    )
    assert "7 (sete) dias corridos" in chunk.content


def test_page_headers_and_footers_are_dropped(chunks):
    assert not any("Página" in c.text or "Manual de Políticas" in c.text for c in chunks)


def test_subsection_spanning_pages_is_kept_whole(chunks):
    sections = _by_section(chunks)
    assert "Jadlog" in sections["5.2"].text
    assert "BR4K7M2X9P1BR" in sections["5.3"].text
