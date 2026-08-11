import sqlite3
import json
import numpy as np

from ai.embeddings import create_embedding

DB_NAME = "second_brain.db"


def cosine_similarity(a, b):

    a = np.array(a)
    b = np.array(b)

    return np.dot(a, b) / (
        np.linalg.norm(a) * np.linalg.norm(b)
    )


def semantic_search(question):

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""

        SELECT

            timestamp,

            app_name,

            window_title,

            summary,

            ocr_text,

            embedding

        FROM memories

    """)

    rows = cursor.fetchall()

    conn.close()

    question_embedding = create_embedding(question)

    scored_memories = []

    for row in rows:

        timestamp = row[0]
        app = row[1]
        title = row[2]
        summary = row[3]
        ocr = row[4]
        embedding_json = row[5]

        if embedding_json is None:
            continue

        embedding = json.loads(embedding_json)

        score = cosine_similarity(

            question_embedding,

            embedding

        )

        scored_memories.append(

            (

                score,

                timestamp,

                app,

                title,

                summary,

                ocr

            )

        )

    scored_memories.sort(

        reverse=True,

        key=lambda x: x[0]

    )

    return scored_memories[:5]
