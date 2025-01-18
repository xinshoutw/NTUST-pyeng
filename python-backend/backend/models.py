from __future__ import annotations  # 允許使用前向引用

from typing import List, Optional

from sqlalchemy import Integer, String, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Entry(Base):
    __tablename__ = 'entries'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    entry_id: Mapped[str] = mapped_column(String, nullable=False)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    question_hash: Mapped[int] = mapped_column(Integer, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    topic: Mapped[str] = mapped_column(String, nullable=False)
    part: Mapped[int] = mapped_column(Integer, nullable=False)

    # 定義與 Choice 的一對多關聯
    choices: Mapped[List[Choice]] = relationship(
        "Choice",
        back_populates="entry",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint('part', 'topic', 'entry_id', name='uix_part_topic_entry_id'),
    )


class Choice(Base):
    __tablename__ = 'choices'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    entry_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('entries.id', ondelete='CASCADE'),
        nullable=False
    )
    choice_text: Mapped[str] = mapped_column(Text, nullable=False)
    choice_order: Mapped[int] = mapped_column(Integer, nullable=False)

    # 定義與 Entry 的多對一關聯
    entry: Mapped[Entry] = relationship(
        "Entry",
        back_populates="choices"
    )

    __table_args__ = (
        UniqueConstraint('entry_id', 'choice_order', name='uix_entry_id_choice_order'),
    )


class Word(Base):
    __tablename__ = 'words'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    part: Mapped[int] = mapped_column(Integer, nullable=False)
    topic: Mapped[str] = mapped_column(String, nullable=False)
    word: Mapped[str] = mapped_column(String, nullable=False)
    pos: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    meaning: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    pronunciations: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON
    definitions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON
    verbs: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON

    __table_args__ = (
        UniqueConstraint('part', 'topic', 'word', name='uix_part_topic_word'),
    )
