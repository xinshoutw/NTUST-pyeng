import hashlib
import json
import os

import uvicorn
from dotenv import load_dotenv
from fastapi import Body, FastAPI, HTTPException, Query
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.params import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import JSONResponse

import models
from database import SessionLocal, engine
from schemas import *

load_dotenv()
HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT"))
REMOTE_HOST = os.getenv("REMOTE_HOST")
REMOTE_PORT = int(os.getenv("REMOTE_PORT"))
BEARER_TOKEN = os.getenv("BEARER_TOKEN")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "")

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="NTUST 英簡單後端",
    description=(
        "提供對題目、單字和習題提供增查功能。\n"
        "可透過本 API 查詢各類 part 與 topic 對應的題目、單字，以及提交新的練習項目。"
    ),
    servers=[{"url": f"https://{REMOTE_HOST}", "description": "公開 API 位址"}],
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    root_path="/api/v1"
)

origins = [origin.strip() for origin in ALLOWED_ORIGINS.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail}, )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(status_code=400, content={"detail": exc.errors()}, )


@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"}, )


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


bearer_scheme = HTTPBearer()


async def verify_bearer_token(
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
):
    if credentials.scheme == "Bearer" and credentials.credentials == BEARER_TOKEN:
        return credentials.credentials
    else:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing Bearer Token",
            headers={"WWW-Authenticate": "Bearer"},
        )


# -----------------------------
# 路由區塊
# -----------------------------

@app.get(
    "/heartbeat",
    summary="心跳檢測",
    description="檢測後端伺服器狀態是否正常可訪問。",
    tags=["Health Check"]
)
async def heartbeat():
    return JSONResponse({"status": "ok"})


@app.get(
    "/practice/{part}/{topic}",
    response_model=PracticeResponse,
    summary="取得練習題目",
    description="根據指定的 `part` 與 `topic`，回傳對應的練習題及選項內容。",
    tags=["Metadata"]
)
async def get_practice(part: int, topic: str, db: Session = Depends(get_db)):
    entries = db.query(models.Entry).filter(
        models.Entry.part == part,
        models.Entry.topic == topic
    ).all()

    # No such practice
    if not entries:
        raise HTTPException(status_code=404, detail="No entries found for the specified part and topic")

    practice_entries = []
    for entry in entries:
        choices = db.query(models.Choice).filter(
            models.Choice.entry_id == entry.id
        ).order_by(models.Choice.choice_order).all()
        choice_schemas = [
            ChoiceSchema(choice_order=choice.choice_order, choice_text=choice.choice_text)
            for choice in choices
        ]
        answer = entry.answer
        if '. ' in answer:
            answer = answer[3:]

        practice_entry = PracticeEntrySchema(
            entry_id=entry.entry_id,
            question=entry.question,
            question_hash=entry.question_hash,
            answer=answer,
            choices=choice_schemas
        )
        practice_entries.append(practice_entry)

    return PracticeResponse(entries=practice_entries)


@app.get(
    "/topics",
    response_model=TopicsResponse,
    summary="取得可用的主題",
    description=(
            "選擇指定 `part` 來篩選符合的主題清單。\n"
            "換句話說，找到具有該回數、週數的可用主題\n"
            "若沒有傳入 `part` 參數，則回傳所有可用的主題。"
    ),
    tags=["Metadata"]
)
async def get_topics(
        part: Optional[int] = Query(None, description="Part number"),
        db: Session = Depends(get_db)
):
    filters = []
    if part:
        filters.append(models.Word.part == part)

    query = db.query(models.Word.topic).distinct()
    if filters:
        query = query.filter(*filters)
    topics = query.all()

    topic_names = [topic[0] for topic in topics]
    if not topic_names:
        raise HTTPException(status_code=404, detail="No topics found for the specified part")

    return TopicsResponse(count=len(topic_names), topics=topic_names)


@app.get(
    "/parts",
    response_model=PartsResponse,
    summary="取得可用的 part",
    description=(
            "選擇指定 `topic` 來篩選符合的 `part` 清單。\n"
            "換句話說，找到具有該主題的回數或是週數\n"
            "若沒有傳入 `topic` 參數，則回傳所有可用的 part。"
    ),
    tags=["Metadata"]
)
async def get_parts(
        topic: Optional[str] = Query(None, description="Topic name"),
        db: Session = Depends(get_db)
):
    filters = []
    if topic:
        filters.append(models.Word.topic == topic)

    query = db.query(models.Word.part).distinct()
    if filters:
        query = query.filter(*filters)
    parts = query.all()

    part_numbers = [part[0] for part in parts]
    if not part_numbers:
        raise HTTPException(status_code=404, detail="No parts found for the specified topic")

    return PartsResponse(count=len(part_numbers), parts=part_numbers)


@app.get(
    "/words",
    response_model=PartResponse,
    summary="取得單字資料",
    description=(
            "可透過 `part` 和 `topic` 兩種 Query 參數來篩選單字。\n"
            "若沒有傳入參數，則回傳關閉該過濾器。"
    ),
    tags=["Metadata"]
)
async def get_words(
        part: Optional[int] = Query(None, description="Part number"),
        topic: Optional[str] = Query(None, description="Topic name"),
        db: Session = Depends(get_db)
):
    # 動態構建過濾條件
    filters = []
    if part:
        filters.append(models.Word.part == part)
    if topic:
        filters.append(models.Word.topic == topic)

    # 查詢數據庫
    query = db.query(models.Word)
    if filters:
        query = query.filter(*filters)
    words = query.all()

    if not words:
        raise HTTPException(status_code=404, detail="No words found for the specified part and topic")

    word_schemas = []
    for word in words:
        pronunciations_data = json.loads(word.pronunciations) if word.pronunciations else []
        definitions_data = json.loads(word.definitions) if word.definitions else []
        verbs_data = json.loads(word.verbs) if word.verbs else []

        pronunciations = [PronunciationSchema(**p) for p in pronunciations_data]

        definitions = []
        for d in definitions_data:
            examples_data = d.get("examples", [])
            examples = [ExampleSchema(**e) for e in examples_data]
            definition = DefinitionSchema(
                pos=d.get("pos"),
                definition=d.get("definition"),
                translation=d.get("translation"),
                examples=examples
            )
            definitions.append(definition)

        verbs = [VerbFormSchema(**v) for v in verbs_data]

        word_schema = WordSchema(
            word=word.word,
            pos=word.pos,
            meaning=word.meaning,
            pronunciations=pronunciations,
            definitions=definitions,
            verbs=verbs
        )
        word_schemas.append(word_schema)

    return PartResponse(words=word_schemas)


@app.post(
    "/add-practices",
    response_model=AddPracticesResponseSchema,
    summary="新增練習題目",
    description=(
            "批次新增練習題目以及對應的選項。\n"
            "需要提供 `Bearer Token` 驗證。"
    ),
    tags=["Admin"]
)
async def add_practices(
        add_request: AddPracticesRequestSchema = Body(...),
        part: int = Query(..., description="Part number"),
        topic: str = Query(..., description="Topic name"),
        db: Session = Depends(get_db),
        token: str = Depends(verify_bearer_token)
):
    added_entries = []
    for entry_id, entry_data in add_request.root.items():
        existing_entry = db.query(models.Entry).filter(
            models.Entry.part == part,
            models.Entry.topic == topic,
            models.Entry.entry_id == entry_id
        ).first()
        if existing_entry:
            raise HTTPException(
                status_code=409,
                detail=f"entry_id '{entry_id}' already exists in part {part} and topic '{topic}'"
            )

        question_hash = int(hashlib.sha256(entry_data.question.encode()).hexdigest()[:8], 16)

        new_entry = models.Entry(
            entry_id=entry_id,
            question=entry_data.question,
            question_hash=question_hash,
            answer=entry_data.answer,
            topic=topic,
            part=part
        )
        db.add(new_entry)
        db.commit()
        db.refresh(new_entry)

        choices = entry_data.choices
        for idx, choice in enumerate(choices, start=1):
            if ": " in choice:
                _, choice_text = choice.split(": ", 1)
            else:
                choice_text = choice
            new_choice = models.Choice(
                entry_id=new_entry.id,
                choice_text=choice_text,
                choice_order=idx
            )
            db.add(new_choice)
        db.commit()

        added_entries.append(entry_id)

    return AddPracticesResponseSchema(
        message="Entries added successfully",
        added_entries=added_entries
    )


@app.post(
    "/add-words",
    response_model=AddWordsResponseSchema,
    summary="新增單字",
    description=(
            "批次新增單字內容。\n"
            "需要提供 `Bearer Token` 驗證。"
    ),
    tags=["Admin"]
)
async def add_words(
        request_data: AddWordsRequestSchema = Body(...),
        db: Session = Depends(get_db),
        token: str = Depends(verify_bearer_token)
):
    """
    批次新增單字到 `words` 表格。請求格式為 JSON，內含 words 的陣列。
    每筆單字須包含 part, topic, word 等欄位。
    若資料庫已有相同 (part, topic, word)，則回傳 409 Conflict。
    """
    added_words = []

    for word_item in request_data.words:
        # 檢查 (part, topic, word) 是否已存在
        existing_word = db.query(models.Word).filter_by(
            part=word_item.part,
            topic=word_item.topic,
            word=word_item.word
        ).first()

        if existing_word:
            raise HTTPException(
                status_code=409,
                detail=f"Word '{word_item.word}' already exists under part {word_item.part} "
                       f"and topic '{word_item.topic}'"
            )

        # 轉換成 JSON 字串存入 DB
        pronunciations_json = json.dumps([p.model_dump() for p in word_item.pronunciations], ensure_ascii=False)
        definitions_json = json.dumps([d.model_dump() for d in word_item.definitions], ensure_ascii=False)
        verbs_json = json.dumps([v.model_dump() for v in word_item.verbs], ensure_ascii=False)

        new_word = models.Word(
            part=word_item.part,
            topic=word_item.topic,
            word=word_item.word,
            pos=word_item.pos,
            meaning=word_item.meaning,
            pronunciations=pronunciations_json,
            definitions=definitions_json,
            verbs=verbs_json
        )
        db.add(new_word)
        db.commit()
        db.refresh(new_word)

        added_words.append(word_item.word)

    return AddWordsResponseSchema(
        message="Words added successfully",
        added_words=added_words
    )


if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)
