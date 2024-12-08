export type Pronunciation = {
    pos: string;
    lang: string;
    url: string;
    pron: string;
};

export type Definition = {
    pos: string;
    definition: string | null;
    translation: string;
};

export type Verb = {
    type: string;
    text: string;
};

export type Word = {
    word: string;
    pos: string | null;
    meaning: string;
    pronunciations: Pronunciation[] | null;
    definitions: Definition[] | null;
    verbs: Verb[] | null;
};

export type PracticeChoice = {
    choice_order: number;
    choice_text: string;
};

export type PracticeEntry = {
    entry_id: string;
    question: string;
    question_hash: number;
    answer: string;
    choices: PracticeChoice[];
};
