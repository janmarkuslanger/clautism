from datetime import date

import pytest

from birthday_flow.people import Person, birthdays_today


def test_parse_full_date_and_age():
    p = Person.from_dict(
        {"name": "Oma", "birthday": "1948-06-23", "relation": "grandparent"}
    )
    assert (p.month, p.day, p.year) == (6, 23, 1948)
    assert p.age_on(date(2026, 6, 23)) == 78


def test_parse_short_date_has_no_year():
    p = Person.from_dict({"name": "Lukas", "birthday": "06-23"})
    assert (p.month, p.day, p.year) == (6, 23, None)
    assert p.age_on(date(2026, 6, 23)) is None


def test_birthday_match():
    p = Person.from_dict({"name": "x", "birthday": "03-12"})
    assert p.has_birthday_on(date(2026, 3, 12))
    assert not p.has_birthday_on(date(2026, 3, 13))


def test_feb29_falls_back_to_feb28_in_non_leap_year():
    p = Person.from_dict({"name": "x", "birthday": "2000-02-29"})
    assert p.has_birthday_on(date(2026, 2, 28))  # 2026 is not a leap year
    assert p.has_birthday_on(date(2028, 2, 29))  # 2028 is a leap year


def test_defaults_applied():
    p = Person.from_dict({"name": "x", "birthday": "01-01"})
    assert p.relation == "default"
    assert p.channel == "telegram"
    assert p.language == "de"


def test_missing_name_raises():
    with pytest.raises(ValueError):
        Person.from_dict({"birthday": "01-01"})


def test_invalid_birthday_raises():
    with pytest.raises(ValueError):
        Person.from_dict({"name": "x", "birthday": "nope"})


def test_to_context_includes_tone_and_age_hint():
    p = Person.from_dict(
        {"name": "Oma", "birthday": "1948-06-23", "relation": "grandparent"}
    )
    ctx = p.to_context(date(2026, 6, 23))
    assert ctx["name"] == "Oma"
    assert "78" in ctx["age_hint"]
    assert ctx["tone"]  # non-empty grandparent tone


def test_birthdays_today_filters():
    people = [
        Person.from_dict({"name": "a", "birthday": "06-23"}),
        Person.from_dict({"name": "b", "birthday": "06-24"}),
    ]
    names = [p.name for p in birthdays_today(people, date(2026, 6, 23))]
    assert names == ["a"]
