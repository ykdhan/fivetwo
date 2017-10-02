DROP TABLE IF EXISTS user;
CREATE TABLE user
(
  id            INTEGER PRIMARY KEY, /* random */
  email         TEXT NOT NULL,
  password      TEXT NOT NULL,
  first_name    TEXT NOT NULL,
  last_name     TEXT NOT NULL,
  gender        TEXT NOT NULL,
  contact       TEXT NOT NULL,
  date_of_birth DATE NOT NULL,
  role          TEXT NOT NULL
);

DROP TABLE IF EXISTS job;
CREATE TABLE job
(
  id             INTEGER PRIMARY KEY, /* random */
  user_id        INTEGER REFERENCES user (id),
  title          TEXT NOT NULL,
  description    TEXT NOT NULL,
  repeated       BOOLEAN NOT NULL,
  job_start_date DATE NULL,
  job_end_date   DATE NULL,
  day            TEXT NULL,
  money          INTEGER NOT NULL,
  every          TEXT NULL,
  accepted       INTEGER REFERENCES application (id)
);

DROP TABLE IF EXISTS application;
CREATE TABLE application
(
  id               INTEGER PRIMARY KEY, /* random */
  user_id          INTEGER REFERENCES user (id),
  job_id           INTEGER REFERENCES job (id),
  application_date DATE NOT NULL
);

DROP TABLE IF EXISTS job_tag;
CREATE TABLE job_tag
(
  user_id        INTEGER REFERENCES user (id),
  job_id         INTEGER REFERENCES job (id),
  PRIMARY KEY (user_id, job_id)
);


DROP TABLE IF EXISTS tag;
CREATE TABLE tag
(
  id              INTEGER PRIMARY KEY, /* random */
  description     TEXT NOT NULL
);


DROP TABLE IF EXISTS password;
CREATE TABLE password
(
  id TEXT PRIMARY KEY, /* random */
  user_id INTEGER REFERENCES user (id)
);