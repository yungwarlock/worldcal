CREATE TABLE calendar_index (
  id SERIAL PRIMARY KEY,
  title TEXT NOT NULL,
  summary TEXT NOT NULL,
  context TEXT NOT NULL, -- JSON
  day INT NOT NULL,
  month INT NOT NULL,
  year INT NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
