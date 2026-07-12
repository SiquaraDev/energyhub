"""Testes de igualdade/hash por identidade da `BaseEntity`."""

from __future__ import annotations

from uuid import uuid4

from energyhub.shared.domain.entity.base_entity import BaseEntity


def test_entities_are_equal_by_id() -> None:
    shared_id = uuid4()
    a = BaseEntity(id=shared_id)
    b = BaseEntity(id=shared_id)
    assert a == b
    assert hash(a) == hash(b)


def test_entities_with_different_ids_are_not_equal() -> None:
    assert BaseEntity() != BaseEntity()


def test_entity_not_equal_to_other_type() -> None:
    assert BaseEntity() != "not-an-entity"


def test_entities_usable_in_a_set() -> None:
    entity = BaseEntity()
    assert len({entity, entity}) == 1
