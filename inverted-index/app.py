import json
import sqlite3
from flask import Flask, request

app = Flask(__name__)
conn = sqlite3.connect('indice_invertido.db', check_same_thread=False)
cursor = conn.cursor()

# Crear la tabla de datos si no existe
cursor.executescript("""
    CREATE TABLE IF NOT EXISTS indice_invertido (
        objeto TEXT NOT NULL,
        video TEXT NOT NULL,
        segundo INTEGER NOT NULL
    );
    
    CREATE VIRTUAL TABLE IF NOT EXISTS indice_invertido_fts USING fts5(
        objeto,
        content='indice_invertido',
        tokenize='unicode61'
    );
    
    -- Trigger para INSERT
    CREATE TRIGGER IF NOT EXISTS indice_invertido_insert
    AFTER INSERT ON indice_invertido
    BEGIN
        INSERT INTO indice_invertido_fts(rowid, objeto)
        VALUES (new.rowid, new.objeto);
    END;

    -- Trigger para UPDATE
    CREATE TRIGGER IF NOT EXISTS indice_invertido_update
    AFTER UPDATE ON indice_invertido
    BEGIN
        UPDATE indice_invertido_fts
        SET objeto = new.objeto
        WHERE rowid = old.rowid;
    END;

    -- Trigger para DELETE
    CREATE TRIGGER IF NOT EXISTS indice_invertido_delete
    AFTER DELETE ON indice_invertido
    BEGIN
        DELETE FROM indice_invertido_fts
        WHERE rowid = old.rowid;
    END;
""")

def process_yolo_data(yolo_data):
    data = []
    for video in yolo_data['videos']:
        video_name = video['video_name']
        for frame in video['frames']:
            timestamp = int(float(frame['timestamp']))
            labels = set()
            for detection in frame['detections']:
                if float(detection['confidence']) > 0.6:
                    labels.add(detection['label'])
            for label in sorted(labels):
                data.append((label, video_name, timestamp))
    return data

def insert_data(data):
    cursor.executemany("""
        INSERT INTO indice_invertido (objeto, video, segundo) VALUES (?, ?, ?)
    """, data)
    conn.commit()

def query_data(query):
    cursor.execute("""
        SELECT i.video, GROUP_CONCAT(i.segundo) FROM indice_invertido_fts fts
        INNER JOIN indice_invertido i ON i.rowid = fts.rowid
        WHERE indice_invertido_fts MATCH ?
        GROUP BY i.video
    """, (query,))
    return cursor.fetchall()
 
def prepare_db_result(db_result):
    result = {'results': []}
    for video, seconds in db_result:
        result['results'].append({
            'video_name': video,
            'seconds': list(map(int, seconds.split(',')))
        })
    return result

@app.get("/")
def app_get():
    query = request.args.get('query')
    if not query:
        return {'status': 'error', 'message': 'query is empty'}, 400
    return prepare_db_result(query_data(query))

@app.post("/receive_metadata")
def app_post():
    data = request.get_json(force=True)
    insert_data(process_yolo_data(data))
    return {"status": "success"}
