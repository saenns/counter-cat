from countercat.classifier import is_affirmative


def test_affirmative_response_parsing():
    assert is_affirmative("YES")
    assert is_affirmative(" yes, a cat is present")
    assert not is_affirmative("NO")
    assert not is_affirmative("yesterday")
