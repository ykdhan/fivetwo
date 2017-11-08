DROP TABLE IF EXISTS user;
CREATE TABLE user
(
  id              INTEGER PRIMARY KEY, /* random */
  email           TEXT NOT NULL,
  password        TEXT NOT NULL,
  name            TEXT NOT NULL,
  gender          TEXT NULL,
  contact         TEXT NULL,
  date_of_birth   DATE NULL,
  introduction    TEXT NULL,
  profile_picture TEXT DEFAULT 'NO',
  is_campus       TEXT DEFAULT 'NO',
  is_registered   TEXT DEFAULT 'NO',
  created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);


DROP TABLE IF EXISTS user_campus;
CREATE TABLE user_campus
(
  id            INTEGER REFERENCES user (id),
  is_student    TEXT DEFAULT 'YES',
  major         TEXT NULL,
  class_year    TEXT NULL,
  department    TEXT NULL,
  position      TEXT NULL,
  created_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
);


DROP TABLE IF EXISTS job;
CREATE TABLE job
(
  id             INTEGER PRIMARY KEY, /* random */
  user_id        INTEGER REFERENCES user (id),
  title          TEXT NOT NULL,
  description    TEXT NOT NULL,
  term           TEXT NOT NULL,
  start_date     DATE NULL,
  end_date       DATE NULL,
  start_time     TIME NULL,
  end_time       TIME NULL,
  day            TEXT NULL,
  money          INTEGER NOT NULL,
  every          TEXT NOT NULL,
  only_campus   TEXT DEFAULT 'NO',
  accepted       INTEGER REFERENCES application (id) DEFAULT 0,
  created_at     DATETIME DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE IF EXISTS application;
CREATE TABLE application
(
  id               INTEGER PRIMARY KEY, /* random */
  user_id          INTEGER REFERENCES user (id),
  job_id           INTEGER REFERENCES job (id),
  created_at     DATETIME DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE IF EXISTS job_tag;
CREATE TABLE job_tag
(
  job_id         INTEGER REFERENCES job (id),
  tag_id         INTEGER REFERENCES tag (id),
  created_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (job_id, tag_id)
);

DROP TABLE IF EXISTS user_tag;
CREATE TABLE user_tag
(
  user_id         INTEGER REFERENCES user (id),
  tag_id         INTEGER REFERENCES tag (id),
  created_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (user_id, tag_id)
);


DROP TABLE IF EXISTS tag;
CREATE TABLE tag
(
  id              INTEGER PRIMARY KEY, /* random */
  description     TEXT NOT NULL,
  created_at     DATETIME DEFAULT CURRENT_TIMESTAMP
);


DROP TABLE IF EXISTS question;
CREATE TABLE question
(
  job_id       INTEGER REFERENCES job (id),
  num          INTEGER NOT NULL,
  question     TEXT NOT NULL,
  created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (job_id, num)
);


DROP TABLE IF EXISTS answer;
CREATE TABLE answer
(
  application_id  INTEGER REFERENCES application (id),
  num             INTEGER NOT NULL,
  answer          TEXT NOT NULL,
  created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (application_id, num)
);


DROP TABLE IF EXISTS password;
CREATE TABLE password
(
  id          TEXT PRIMARY KEY, /* random */
  user_id     INTEGER REFERENCES user (id),
  created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);