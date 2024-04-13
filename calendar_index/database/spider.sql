CREATE TABLE spider_index (
  hash SERIAL PRIMARY KEY,
  title TEXT NOT NULL,
  url TEXT NOT NULL,
  date_added TIMESTAMP NOT NULL DEFAULT NOW(),
  previous_node_hash TEXT NOT NULL DEFAULT 'origin'
);