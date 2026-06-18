Legal RAG Agent

RAG-агент для поиска и анализа нормативных документов с использованием гибридного поиска (BM25 + Dense Retrieval) и локальной LLM через Ollama.

Возможности

* Загрузка PDF и DOCX документов
* Автоматическое построение структуры документа:
    * Глава
    * Раздел
    * Статья
    * Пункт
* Sparse Retrieval (BM25)
* Dense Retrieval (Embeddings)
* Hybrid Search
* Chunk Graph:
    * parent → child
    * sibling navigation
* ReAct Agent с инструментами:
    * retrieve()
    * read_chunk()
    * expand_path()
    * get_neighbors()
* Веб-интерфейс на FastAPI
* Поддержка локальных моделей через Ollama

⸻

Архитектура

Документы
    ↓
Парсер
    ↓
Chunk Graph
    ↓
BM25 + Dense Index
    ↓
Hybrid Retriever
    ↓
Tools
    ↓
ReAct Agent
    ↓
LLM

⸻

Структура проекта

project/
├── app.py
├── agent.py
├── client.py
├── kb.py
├── tools.py
├── uploads/
├── frontend/
│   └── index.html
├── requirements.txt
└── README.md

⸻

Установка

1. Клонирование репозитория

git clone <repo_url>
cd <repo_name>

2. Создание виртуального окружения

macOS / Linux

python3 -m venv venv
source venv/bin/activate

Windows

python -m venv venv
venv\Scripts\activate

3. Установка зависимостей

pip install -r requirements.txt

⸻

Установка модели

Установить Ollama:

https://ollama.com

Скачать модель:

ollama pull qwen2.5:7b

Запустить Ollama:

ollama serve

⸻

Запуск приложения

Запуск веб-сервера:

uvicorn app:app --reload

После запуска открыть:

http://localhost:8000

Swagger-документация:

http://localhost:8000/docs

⸻

Использование

Шаг 1

Загрузить PDF или DOCX документы через веб-интерфейс.

Шаг 2

Нажать кнопку:

Инициализировать базу

Будут построены:

* Chunk Graph
* BM25 Index
* Dense Index

Шаг 3

Задать вопрос на естественном языке.

Пример:

Каков срок подачи декларации по НДС?

⸻

Конфигурация агента

Настройки находятся непосредственно в файлах проекта.

Выбор модели

В app.py:

agent = Agent(
    client=client,
    kb=kb,
    tools=TOOLS,
    tool_schemas=tool_schemas,
    model="qwen2.5:7b",
    temperature=0.0,
    max_steps=10
)

Изменить модель:

model="llama3:8b"

или

model="gemma3:4b"

⸻

Температура

temperature=0.0

Рекомендуемые значения:

Значение	Назначение
0.0	Максимальная точность
0.2	Небольшая вариативность
0.7	Более творческие ответы

⸻

Максимальное число шагов агента

max_steps=10

Обычно достаточно:

5-10

⸻

Поддерживаемые форматы

* PDF
* DOCX

⸻

Скриншоты

Главная страница

Загрузка документов

Ответ агента

⸻

Ограничения

* Качество ответа зависит от качества структуры документа.
* Документы со сложной версткой могут разбираться неидеально.
* Большие коллекции документов требуют дополнительной оптимизации индекса.
* Индексация большого количества документов может занимать некоторое время.

⸻

Планы развития

* Streaming ответов
* История диалога
* Подсветка источников
* Ранжирование по документам
* Экспорт ответов
* Docker-образ
* Поддержка OpenRouter
* Мультимодальный поиск

⸻

Лицензия

MIT
