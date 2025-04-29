CREATE VIRTUAL TABLE indice_invertido_fts USING fts5(
    objeto,
    content='indice_invertido',
    tokenize='unicode61'
);

CREATE TABLE indice_invertido (
	objeto	TEXT NOT NULL,
	video	TEXT NOT NULL,
	segundo	INTEGER NOT NULL
);

-- Insertar objeto en tabla principal
INSERT INTO indice_invertido (objeto, video, frame) VALUES ('persona', 'video1.mp4', 123);

SELECT video, frame
FROM indice_invertido_fts
WHERE objeto MATCH 'persona';