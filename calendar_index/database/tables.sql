CREATE TYPE job_status AS ENUM ('not_scheduled', 'scheduled', 'completed', 'failed');

CREATE TABLE spider_index  (
  id SERIAL PRIMARY KEY,
  hash TEXT NOT NULL,
  url TEXT NOT NULL,
  category TEXT NOT NULL DEFAULT 'unknown',
  date_added TIMESTAMP NOT NULL DEFAULT NOW(),
  status job_status NOT NULL DEFAULT 'not_scheduled',
  previous_node_hash TEXT NOT NULL DEFAULT 'origin'
);

CREATE TABLE calendar_index (
  id SERIAL PRIMARY KEY,
  title TEXT NOT NULL,
  summary TEXT NOT NULL,
  url_id INT NOT NULL,
  context JSONB NOT NULL, -- JSON
  day INT NOT NULL,
  month INT NOT NULL,
  year INT NOT NULL,
  date_added TIMESTAMP NOT NULL DEFAULT NOW(),
  FOREIGN KEY (url_id) REFERENCES spider_index(id)
);
