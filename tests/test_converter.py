from dot2mmd import Dot2Mermaid

def test_basic_conversion():
    dot_text = """
    digraph G {
        A [label="Start"];
        B [label="End"];
        A -> B;
    }
    """
    converter = Dot2Mermaid(dot_text)
    mermaid = converter.convert()
    assert "A" in mermaid and "B" in mermaid
    assert "-->" in mermaid
