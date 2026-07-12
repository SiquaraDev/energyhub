"""Regressão da BaseEntity: subclasses com campos obrigatórios e timestamps."""

from dataclasses import dataclass

from energyhub.shared.domain.entity.base_entity import BaseEntity


@dataclass
class _SampleEntity(BaseEntity):
    """Entidade de teste com um campo obrigatório (valida kw_only na base)."""

    name: str


def test_base_entity_has_defaults() -> None:
    entity = BaseEntity()
    assert entity.id is not None
    assert entity.created_at is not None
    assert entity.updated_at is not None


def test_subclass_with_required_field_instantiates() -> None:
    # Sem kw_only na base, isto falharia na definição da classe (TypeError).
    sample = _SampleEntity(name="EnergyHub")
    assert sample.name == "EnergyHub"
    assert sample.id is not None  # herdado, keyword-only com default


def test_update_timestamp_advances() -> None:
    entity = BaseEntity()
    before = entity.updated_at
    entity.update_timestamp()
    assert entity.updated_at >= before


def test_post_init_handles_explicit_none() -> None:
    entity = BaseEntity(id=None, created_at=None, updated_at=None)  # type: ignore[arg-type]
    assert entity.id is not None
    assert entity.created_at is not None
    assert entity.updated_at is not None
