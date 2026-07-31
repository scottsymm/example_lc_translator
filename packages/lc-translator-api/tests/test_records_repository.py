"""Tests for RecordRepository."""

from __future__ import annotations

from lc_translator_api.repositories.record import RecordRepository
from lc_translator_api.schemas.record import RecordCreate, RecordUpdate


def test_create_record(repository: RecordRepository, sample_create: RecordCreate) -> None:
    record = repository.create(sample_create)
    assert record.id
    assert record.source_type == "generated"
    assert record.title.startswith("LC Record")


def test_get_record(repository: RecordRepository, sample_create: RecordCreate) -> None:
    created = repository.create(sample_create)
    fetched = repository.get(created.id)
    assert fetched is not None
    assert fetched.id == created.id


def test_get_missing_record(repository: RecordRepository) -> None:
    assert repository.get("not-a-real-id") is None


def test_list_records(repository: RecordRepository, sample_create: RecordCreate) -> None:
    repository.create(sample_create)
    repository.create(sample_create)
    records = repository.list(limit=10)
    assert len(records) == 2


def test_list_filter_by_source_type(
    repository: RecordRepository, sample_create: RecordCreate
) -> None:
    repository.create(sample_create)
    repository.create(RecordCreate(source_type="translated", mt700_input="MT700"))
    generated = repository.list(source_type="generated")
    translated = repository.list(source_type="translated")
    assert len(generated) == 1
    assert len(translated) == 1


def test_update_record(repository: RecordRepository, sample_create: RecordCreate) -> None:
    created = repository.create(sample_create)
    updated = repository.update(created.id, RecordUpdate(title="New Title"))
    assert updated is not None
    assert updated.title == "New Title"


def test_update_missing_record(repository: RecordRepository) -> None:
    assert repository.update("missing-id", RecordUpdate(title="X")) is None


def test_delete_record(repository: RecordRepository, sample_create: RecordCreate) -> None:
    created = repository.create(sample_create)
    assert repository.delete(created.id) is True
    assert repository.get(created.id) is None


def test_delete_missing_record(repository: RecordRepository) -> None:
    assert repository.delete("missing-id") is False
