CREATE TYPE job_status AS ENUM ('not_scheduled', 'scheduled', 'completed');

CREATE TABLE spider_index  (
  id SERIAL PRIMARY KEY,
  hash TEXT NOT NULL,
  title TEXT NOT NULL,
  url TEXT NOT NULL,
  date_added TIMESTAMP NOT NULL DEFAULT NOW(),
  previous_node_hash TEXT NOT NULL DEFAULT 'origin'
);

CREATE spider_job_queue (
  id SERIAL PRIMARY KEY,
  spider_index_id INT NOT NULL,
  date_added TIMESTAMP NOT NULL DEFAULT NOW(),
  status job_status NOT NULL DEFAULT 'not_scheduled'
);

CREATE TABLE calendar_index (
  id SERIAL PRIMARY KEY,
  title TEXT NOT NULL,
  summary TEXT NOT NULL,
  context JSONB NOT NULL, -- JSON
  day INT NOT NULL,
  month INT NOT NULL,
  year INT NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE calendar_job_queue (
  id SERIAL PRIMARY KEY,
  spider_index_id INT NOT NULL,
  date_added TIMESTAMP NOT NULL DEFAULT NOW(),
  status job_status NOT NULL DEFAULT 'not_scheduled'
);
