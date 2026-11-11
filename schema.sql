-- Создание базы данных (выполнять в psql или DBeaver отдельно, если БД еще нет)
-- CREATE DATABASE laboratory_3;

-- 1. СПРАВОЧНИКИ
CREATE TABLE specialties (
    id    SERIAL PRIMARY KEY,
    name  VARCHAR(150) NOT NULL UNIQUE
);

CREATE TABLE education_levels (
    id    SERIAL PRIMARY KEY,
    name  VARCHAR(100) NOT NULL UNIQUE,
    rank  SMALLINT NOT NULL UNIQUE
);

CREATE TABLE unemployment_reasons (
    id    SERIAL PRIMARY KEY,
    name  VARCHAR(150) NOT NULL UNIQUE
);

CREATE TABLE skills (
    id    SERIAL PRIMARY KEY,
    name  VARCHAR(100) NOT NULL UNIQUE
);

-- 2. БЕЗРАБОТНЫЕ
CREATE TABLE unemployed (
    id                    SERIAL PRIMARY KEY,
    full_name             VARCHAR(200) NOT NULL,
    gender                CHAR(1) NOT NULL CHECK (gender IN ('M','F')),
    birth_date            DATE NOT NULL,
    city                  VARCHAR(100),
    street                VARCHAR(150),
    building              VARCHAR(20),
    apartment             VARCHAR(20),
    education_level_id    INT REFERENCES education_levels(id),
    education_institution VARCHAR(300),
    specialty_id          INT REFERENCES specialties(id),
    experience_years      SMALLINT NOT NULL DEFAULT 0 CHECK (experience_years BETWEEN 0 AND 70),
    reason_id             INT REFERENCES unemployment_reasons(id),
    phone                 VARCHAR(30),
    email                 VARCHAR(100),
    telegram              VARCHAR(100),
    vk                    VARCHAR(150),
    max_messenger         VARCHAR(100),
    expected_salary       NUMERIC(12,2),
    registered_at         DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at            TIMESTAMP NOT NULL DEFAULT now()
);

-- 3. ПРЕДПРИЯТИЯ
CREATE TABLE enterprises (
    id         SERIAL PRIMARY KEY,
    name       VARCHAR(200) NOT NULL,
    city       VARCHAR(100),
    street     VARCHAR(150),
    building   VARCHAR(20),
    apartment  VARCHAR(20),
    phone      VARCHAR(30),
    email      VARCHAR(100),
    website    VARCHAR(200),
    telegram   VARCHAR(150),
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

-- 4. ВАКАНСИИ
CREATE TABLE vacancies (
    id                   SERIAL PRIMARY KEY,
    enterprise_id        INT NOT NULL REFERENCES enterprises(id) ON DELETE CASCADE,
    specialty_id         INT NOT NULL REFERENCES specialties(id),
    title                VARCHAR(200),
    education_level_id   INT REFERENCES education_levels(id),
    min_experience_years SMALLINT NOT NULL DEFAULT 0,
    gender               CHAR(1) CHECK (gender IN ('M','F') OR gender IS NULL),
    min_age              SMALLINT CHECK (min_age BETWEEN 14 AND 100),
    max_age              SMALLINT CHECK (max_age BETWEEN 14 AND 100),
    work_day             VARCHAR(100),
    weekends             VARCHAR(100),
    vacation_days        SMALLINT,
    salary_min           NUMERIC(12,2),
    salary_max           NUMERIC(12,2),
    benefits             TEXT,
    description          TEXT,
    is_active            BOOLEAN NOT NULL DEFAULT TRUE,
    created_at           TIMESTAMP NOT NULL DEFAULT now(),
    CHECK (max_age IS NULL OR min_age IS NULL OR max_age >= min_age),
    CHECK (salary_max IS NULL OR salary_min IS NULL OR salary_max >= salary_min)
);

-- 5. СВЯЗУЮЩИЕ ТАБЛИЦЫ
CREATE TABLE unemployed_skills (
    unemployed_id  INT NOT NULL REFERENCES unemployed(id) ON DELETE CASCADE,
    skill_id       INT NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    PRIMARY KEY (unemployed_id, skill_id)
);

CREATE TABLE vacancy_skills (
    vacancy_id   INT NOT NULL REFERENCES vacancies(id) ON DELETE CASCADE,
    skill_id     INT NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    is_required  BOOLEAN NOT NULL DEFAULT TRUE,
    PRIMARY KEY (vacancy_id, skill_id)
);

-- 6. ИНДЕКСЫ
CREATE INDEX idx_unemployed_specialty ON unemployed(specialty_id);
CREATE INDEX idx_unemployed_education ON unemployed(education_level_id);
CREATE INDEX idx_unemployed_city      ON unemployed(city);
CREATE INDEX idx_enterprises_city     ON enterprises(city);
CREATE INDEX idx_vacancies_enterprise ON vacancies(enterprise_id);
CREATE INDEX idx_vacancies_specialty  ON vacancies(specialty_id);
CREATE INDEX idx_vacancies_active     ON vacancies(is_active);

-- 7. СТАРТОВЫЕ ДАННЫЕ СПРАВОЧНИКОВ
INSERT INTO education_levels (name, rank) VALUES
 ('Начальное', 1), ('Среднее', 2), ('Среднее специальное', 3),
 ('Неоконченное высшее', 4), ('Бакалавр', 5), ('Магистр / Специалист', 6),
 ('Кандидат наук', 7), ('Доктор наук', 8);

INSERT INTO unemployment_reasons (name) VALUES
 ('Сокращение штата'), ('Собственное желание'), ('Переезд'),
 ('Болезнь'), ('Окончание учебного заведения'), ('Ликвидация предприятия'), ('Другое');

INSERT INTO skills (name) VALUES
 ('Английский язык'), ('Немецкий язык'), ('Знание ПК (уверенный пользователь)'),
 ('MS Excel'), ('1С'), ('Водительские права B'), ('Работа с клиентами'), ('Управление проектами');

INSERT INTO specialties (name) VALUES
 ('Менеджер'), ('Бухгалтер'), ('Инженер-программист'), ('Водитель'), ('Продавец'), ('Экономист'), ('Юрист');