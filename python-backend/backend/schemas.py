from dataclasses import field
from typing import List, Optional, Dict

from pydantic import BaseModel, RootModel


class ExampleSchema(BaseModel):
    text: str
    translation: Optional[str] = None


class PartsResponse(BaseModel):
    count: int
    parts: List[int]

    class Config:
        from_attributes = True


class DefinitionSchema(BaseModel):
    pos: Optional[str] = None
    definition: Optional[str] = None
    translation: Optional[str] = None
    examples: List[ExampleSchema] = field(default_factory=list)

    class Config:
        from_attributes = True


class PronunciationSchema(BaseModel):
    pos: Optional[str] = None
    lang: Optional[str] = None
    url: Optional[str] = None
    pron: Optional[str] = None


class VerbFormSchema(BaseModel):
    type: Optional[str] = None
    text: Optional[str] = None


class WordSchema(BaseModel):
    word: str
    pos: Optional[str] = None
    meaning: Optional[str] = None
    pronunciations: List[PronunciationSchema] = field(default_factory=list)
    definitions: List[DefinitionSchema] = field(default_factory=list)
    verbs: List[VerbFormSchema] = field(default_factory=list)

    class Config:
        from_attributes = True


class PartResponse(BaseModel):
    words: List[WordSchema]

    class Config:
        from_attributes = True


class ChoiceSchema(BaseModel):
    choice_order: int
    choice_text: str

    class Config:
        from_attributes = True


class PracticeEntrySchema(BaseModel):
    entry_id: str
    question: str
    question_hash: int
    answer: str
    choices: List[ChoiceSchema]

    class Config:
        from_attributes = True


class PracticeResponse(BaseModel):
    entries: List[PracticeEntrySchema]

    class Config:
        from_attributes = True


class TopicsResponse(BaseModel):
    count: int
    topics: List[str]

    class Config:
        from_attributes = True


class EntryCreateSchema(BaseModel):
    question: str
    answer: str
    choices: List[str]

    class Config:
        from_attributes = True


class AddPracticesRequestSchema(RootModel[Dict[str, EntryCreateSchema]]):
    pass


class AddPracticesResponseSchema(BaseModel):
    message: str
    added_entries: List[str]

    class Config:
        from_attributes = True


class WordCreateSchema(BaseModel):
    part: int
    topic: str
    word: str
    pos: Optional[str] = None
    meaning: Optional[str] = None
    pronunciations: List[PronunciationSchema] = field(default_factory=list)
    definitions: List[DefinitionSchema] = field(default_factory=list)
    verbs: List[VerbFormSchema] = field(default_factory=list)


class AddWordsRequestSchema(BaseModel):
    words: List[WordCreateSchema]


class AddWordsResponseSchema(BaseModel):
    message: str
    added_words: List[str]
