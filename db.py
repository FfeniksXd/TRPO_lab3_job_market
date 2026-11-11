import psycopg2

class Database:
    def __init__(self):
        self.conn_params = {
            "dbname": "laboratory_3",
            "user": "postgres",
            "password": "7ujm7UJM",  
            "host": "localhost",
            "port": "5432"
        }

    # --- ЧТЕНИЕ (SELECT) ---
    def execute_query(self, query, params=None):
        """Выполняет SELECT-запрос и возвращает список кортежей"""
        with psycopg2.connect(**self.conn_params) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()

    # --- ИЗМЕНЕНИЕ (INSERT, UPDATE, DELETE) ---
    def execute_dml(self, query, params=None):
        """Выполняет запросы, которые меняют данные. Ничего не возвращает."""
        with psycopg2.connect(**self.conn_params) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                # Благодаря 'with' коммит (сохранение) произойдет автоматически

    def get_specialties(self):
        return self.execute_query("SELECT id, name FROM specialties ORDER BY name")
        
    # ---   методы для CRUD ---
    def add_specialty(self, name):
        self.execute_dml("INSERT INTO specialties (name) VALUES (%s)", (name,))

    def update_specialty(self, spec_id, name):
        self.execute_dml("UPDATE specialties SET name = %s WHERE id = %s", (name, spec_id))

    def delete_specialty(self, spec_id):
        self.execute_dml("DELETE FROM specialties WHERE id = %s", (spec_id,))

        # --- МЕТОДЫ ДЛЯ ПРЕДПРИЯТИЙ ---
    def get_enterprises(self):
        # Возвращаем ID, Название, Город, Телефон, Сайт (для таблицы)
        return self.execute_query(
            "SELECT id, name, city, phone, website FROM enterprises ORDER BY name"
        )

    def add_enterprise(self, name, city, street, building, phone, email, website, telegram):
        self.execute_dml(
            """INSERT INTO enterprises 
               (name, city, street, building, phone, email, website, telegram) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (name, city, street, building, phone, email, website, telegram)
        )

    def update_enterprise(self, ent_id, name, city, street, building, phone, email, website, telegram):
        self.execute_dml(
            """UPDATE enterprises 
               SET name=%s, city=%s, street=%s, building=%s, phone=%s, email=%s, website=%s, telegram=%s 
               WHERE id=%s""",
            (name, city, street, building, phone, email, website, telegram, ent_id)
        )

    def delete_enterprise(self, ent_id):
        # Поскольку в БД стоит ON DELETE CASCADE, 
        # поэтому при удалении предприятия удалятся и его вакансии!
        self.execute_dml("DELETE FROM enterprises WHERE id = %s", (ent_id,))

        # --- ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ДЛЯ СПРАВОЧНИКОВ ---
    def get_education_levels(self):
        return self.execute_query("SELECT id, name FROM education_levels ORDER BY rank")

    def get_unemployment_reasons(self):
        return self.execute_query("SELECT id, name FROM unemployment_reasons ORDER BY name")

    def get_skills(self):
        return self.execute_query("SELECT id, name FROM skills ORDER BY name")

    # --- МЕТОДЫ ДЛЯ БЕЗРАБОТНЫХ ---
    def get_unemployed(self):
        """Возвращает список безработных с названиями специальностей и образований (через JOIN)"""
        query = """
            SELECT u.id, u.full_name, u.gender, u.birth_date, u.city, 
                   e.name AS education, s.name AS specialty
            FROM unemployed u
            LEFT JOIN education_levels e ON u.education_level_id = e.id
            LEFT JOIN specialties s ON u.specialty_id = s.id
            ORDER BY u.full_name
        """
        return self.execute_query(query)

    def get_unemployed_by_id(self, u_id):
        """Возвращает полные данные одного безработного и список его ID навыков"""
        query = """
            SELECT id, full_name, gender, birth_date, city, street, building, apartment,
                   education_level_id, education_institution, specialty_id, experience_years,
                   reason_id, phone, email, telegram, vk, max_messenger, expected_salary
            FROM unemployed WHERE id = %s
        """
        data = self.execute_query(query, (u_id,))[0]
        
        # Отдельно достаем навыки
        skills = self.execute_query("SELECT skill_id FROM unemployed_skills WHERE unemployed_id = %s", (u_id,))
        skill_ids = [s[0] for s in skills]
        
        return data, skill_ids

    def add_unemployed(self, data, skill_ids):
        """Добавляет безработного и его навыки в одной транзакции"""
        query = """
            INSERT INTO unemployed 
            (full_name, gender, birth_date, city, street, building, apartment,
             education_level_id, education_institution, specialty_id, experience_years,
             reason_id, phone, email, telegram, vk, max_messenger, expected_salary)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        import psycopg2
        with psycopg2.connect(**self.conn_params) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, data)
                new_id = cursor.fetchone()[0] # Получаем ID нового безработного
                
                # Сохраняем навыки
                for s_id in skill_ids:
                    cursor.execute(
                        "INSERT INTO unemployed_skills (unemployed_id, skill_id) VALUES (%s, %s)",
                        (new_id, s_id)
                    )

    def update_unemployed(self, u_id, data, skill_ids):
        """Обновляет данные безработного и полностью перезаписывает его навыки"""
        query = """
            UPDATE unemployed SET 
            full_name=%s, gender=%s, birth_date=%s, city=%s, street=%s, building=%s, apartment=%s,
            education_level_id=%s, education_institution=%s, specialty_id=%s, experience_years=%s,
            reason_id=%s, phone=%s, email=%s, telegram=%s, vk=%s, max_messenger=%s, expected_salary=%s
            WHERE id=%s
        """
        import psycopg2
        with psycopg2.connect(**self.conn_params) as conn:
            with conn.cursor() as cursor:
                # Добавляем u_id в конец кортежа данных для WHERE id=%s
                cursor.execute(query, data + (u_id,))
                
                # Удаляем старые навыки и записываем новые (самый простой способ обновления)
                cursor.execute("DELETE FROM unemployed_skills WHERE unemployed_id = %s", (u_id,))
                for s_id in skill_ids:
                    cursor.execute(
                        "INSERT INTO unemployed_skills (unemployed_id, skill_id) VALUES (%s, %s)",
                        (u_id, s_id)
                    )

    def delete_unemployed(self, u_id):
        self.execute_dml("DELETE FROM unemployed WHERE id = %s", (u_id,))

        # --- МЕТОДЫ ДЛЯ ВАКАНСИЙ ---
    def get_vacancies(self):
        query = """
            SELECT v.id, e.name as enterprise, s.name as specialty, v.title, 
                   v.salary_min, v.salary_max, v.is_active
            FROM vacancies v
            JOIN enterprises e ON v.enterprise_id = e.id
            JOIN specialties s ON v.specialty_id = s.id
            ORDER BY e.name, s.name
        """
        return self.execute_query(query)

    def get_vacancy_by_id(self, v_id):
        query = """
            SELECT enterprise_id, specialty_id, title, education_level_id, 
                   min_experience_years, gender, min_age, max_age, 
                   work_day, weekends, vacation_days, salary_min, salary_max, 
                   benefits, description, is_active
            FROM vacancies WHERE id = %s
        """
        data = self.execute_query(query, (v_id,))[0]
        
        # Достаем навыки с флагом обязательности
        skills = self.execute_query("SELECT skill_id, is_required FROM vacancy_skills WHERE vacancy_id = %s", (v_id,))
        # Превращаем в словарь: {id_навыка: True/False}
        skills_dict = {s[0]: s[1] for s in skills}
        
        return data, skills_dict

    def add_vacancy(self, data, skills_dict):
        query = """
            INSERT INTO vacancies 
            (enterprise_id, specialty_id, title, education_level_id, 
             min_experience_years, gender, min_age, max_age, 
             work_day, weekends, vacation_days, salary_min, salary_max, 
             benefits, description, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        import psycopg2
        with psycopg2.connect(**self.conn_params) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, data)
                new_id = cursor.fetchone()[0]
                
                for skill_id, is_req in skills_dict.items():
                    cursor.execute(
                        "INSERT INTO vacancy_skills (vacancy_id, skill_id, is_required) VALUES (%s, %s, %s)",
                        (new_id, skill_id, is_req)
                    )

    def update_vacancy(self, v_id, data, skills_dict):
        query = """
            UPDATE vacancies SET 
            enterprise_id=%s, specialty_id=%s, title=%s, education_level_id=%s,
            min_experience_years=%s, gender=%s, min_age=%s, max_age=%s,
            work_day=%s, weekends=%s, vacation_days=%s, salary_min=%s, salary_max=%s,
            benefits=%s, description=%s, is_active=%s
            WHERE id=%s
        """
        import psycopg2
        with psycopg2.connect(**self.conn_params) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, data + (v_id,))
                
                # Обновляем навыки (удаляем старые, пишем новые)
                cursor.execute("DELETE FROM vacancy_skills WHERE vacancy_id = %s", (v_id,))
                for skill_id, is_req in skills_dict.items():
                    cursor.execute(
                        "INSERT INTO vacancy_skills (vacancy_id, skill_id, is_required) VALUES (%s, %s, %s)",
                        (v_id, skill_id, is_req)
                    )

    def delete_vacancy(self, v_id):
        self.execute_dml("DELETE FROM vacancies WHERE id = %s", (v_id,))

        # --- МЕТОД ДЛЯ ОТЧЕТОВ ---
    def get_report_data(self, report_type):
        """Возвращает заголовки и данные для выбранного отчета"""
        
        # 1. Группировка по возрасту
        if report_type == "age":
            query = """
                SELECT 
                    CASE 
                        WHEN EXTRACT(YEAR FROM AGE(birth_date)) < 25 THEN 'До 25 лет'
                        WHEN EXTRACT(YEAR FROM AGE(birth_date)) BETWEEN 25 AND 35 THEN '25-35 лет'
                        WHEN EXTRACT(YEAR FROM AGE(birth_date)) BETWEEN 36 AND 45 THEN '36-45 лет'
                        WHEN EXTRACT(YEAR FROM AGE(birth_date)) BETWEEN 46 AND 55 THEN '46-55 лет'
                        ELSE 'Старше 55 лет'
                    END AS age_group,
                    COUNT(*) AS count
                FROM unemployed
                GROUP BY age_group
                ORDER BY count DESC
            """
            headers = ["Возрастная группа", "Количество человек"]
            
        # 2. Группировка по полу
        elif report_type == "gender":
            query = """
                SELECT 
                    CASE WHEN gender = 'M' THEN 'Мужчины' ELSE 'Женщины' END AS gender_name,
                    COUNT(*) AS count
                FROM unemployed
                GROUP BY gender
            """
            headers = ["Пол", "Количество человек"]
            
        # 3. Группировка по образованию
        elif report_type == "education":
            query = """
                SELECT e.name AS education, COUNT(u.id) AS count
                FROM education_levels e
                LEFT JOIN unemployed u ON u.education_level_id = e.id
                GROUP BY e.name, e.rank
                ORDER BY e.rank DESC
            """
            headers = ["Уровень образования", "Количество человек"]
            
        # 4. Группировка по специальности
        elif report_type == "specialty":
            query = """
                SELECT s.name AS specialty, COUNT(u.id) AS count
                FROM specialties s
                LEFT JOIN unemployed u ON u.specialty_id = s.id
                GROUP BY s.name
                ORDER BY count DESC, s.name
            """
            headers = ["Специальность", "Количество человек"]
            
        # 5. Группировка по стажу
        elif report_type == "experience":
            query = """
                SELECT 
                    CASE 
                        WHEN experience_years = 0 THEN 'Нет стажа'
                        WHEN experience_years BETWEEN 1 AND 3 THEN '1-3 года'
                        WHEN experience_years BETWEEN 4 AND 5 THEN '4-5 лет'
                        WHEN experience_years BETWEEN 6 AND 10 THEN '6-10 лет'
                        ELSE 'Более 10 лет'
                    END AS exp_group,
                    COUNT(*) AS count
                FROM unemployed
                GROUP BY exp_group
                ORDER BY count DESC
            """
            headers = ["Стаж работы", "Количество человек"]
            
        else:
            return [], []

        data = self.execute_query(query)
        return headers, data

        # --- МЕТОДЫ ДЛЯ ПОДБОРА ---
    def get_unemployed_list(self):
        """Список безработных для выпадающего списка (ID + ФИО)"""
        return self.execute_query("SELECT id, full_name FROM unemployed ORDER BY full_name")

    def get_matching_vacancies(self, u_id):
        """Возвращает список подходящих вакансий с рассчитанным баллом соответствия"""
        
        # 1. Получаем данные безработного и его навыки
        u_data = self.execute_query(
            "SELECT gender, EXTRACT(YEAR FROM AGE(birth_date)), experience_years, expected_salary FROM unemployed WHERE id = %s", 
            (u_id,)
        )[0]
        u_gender, u_age, u_exp, u_expected_salary = u_data
        u_age = int(u_age) if u_age else 0

        u_skills_rows = self.execute_query("SELECT skill_id FROM unemployed_skills WHERE unemployed_id = %s", (u_id,))
        u_skills = set(row[0] for row in u_skills_rows)

        # 2. SQL-запрос с ЖЕСТКИМИ фильтрами (специальность, образование, обязательные навыки)
        query = """
            SELECT 
                v.id, e.name AS enterprise, v.title, s.name AS specialty,
                v.min_experience_years, v.gender AS req_gender, 
                v.min_age, v.max_age, v.salary_min, v.salary_max, v.description
            FROM vacancies v
            JOIN enterprises e ON v.enterprise_id = e.id
            JOIN specialties s ON v.specialty_id = s.id
            JOIN unemployed u ON u.id = %s
            LEFT JOIN education_levels ve ON v.education_level_id = ve.id
            LEFT JOIN education_levels ue ON u.education_level_id = ue.id
            WHERE v.is_active = TRUE 
              AND v.specialty_id = u.specialty_id
              AND (ve.rank IS NULL OR ue.rank >= ve.rank)
              AND NOT EXISTS (
                  SELECT 1 FROM vacancy_skills vs
                  WHERE vs.vacancy_id = v.id AND vs.is_required = TRUE
                    AND vs.skill_id NOT IN (SELECT skill_id FROM unemployed_skills WHERE unemployed_id = u.id)
              )
        """
        vacancies = self.execute_query(query, (u_id,))
        
        results = []
        for v in vacancies:
            v_id, ent_name, title, spec_name, min_exp, req_gender, min_age, max_age, sal_min, sal_max, desc = v
            
            # 3. Рассчитываем балл (от 0 до 100)
            score = 50 # Базовый балл за прохождение жестких фильтров
            
            # Стаж (макс +20)
            if min_exp and u_exp >= min_exp:
                score += 20
            elif min_exp and min_exp > 0:
                score += int((u_exp / min_exp) * 20) # Частичный балл, если стажа чуть меньше
                
            # Возраст (макс +10)
            age_ok = True
            if min_age and u_age < min_age: age_ok = False
            if max_age and u_age > max_age: age_ok = False
            if age_ok: score += 10
            
            # Пол (макс +5)
            if not req_gender or req_gender == u_gender:
                score += 5
                
            # Зарплата (макс +15)
            if not u_expected_salary:
                score += 15 # Если безработный не указал ожидания, даем полный балл
            elif sal_max and sal_max >= u_expected_salary:
                score += 15
            elif sal_min and sal_min >= u_expected_salary:
                score += 10
            elif sal_max and sal_max < u_expected_salary:
                score += 0 # Зарплата ниже ожиданий
                
            # Желательные навыки (макс +10)
            req_skills_rows = self.execute_query("SELECT skill_id FROM vacancy_skills WHERE vacancy_id = %s AND is_required = FALSE", (v_id,))
            desired_skills = set(row[0] for row in req_skills_rows)
            if desired_skills:
                matched = len(desired_skills.intersection(u_skills))
                score += min(10, int((matched / len(desired_skills)) * 10))
            else:
                score += 10 # Если нет пожеланий, даем макс балл
                
            # Ограничиваем максимум до 100
            score = min(100, score)

            # Рекомендуем вакансии, где совпадение больше 60%
            if score >= 60:
                results.append((
                    score, v_id, ent_name, title or spec_name, 
                    f"{sal_min or 0} - {sal_max or 0}", desc or ""
                ))
                
        # Сортируем по убыванию балла
        results.sort(key=lambda x: x[0], reverse=True)
        return results

    def get_vacancies_list(self):
        """Список активных вакансий для выпадающего списка (ID + Название)"""
        query = """
            SELECT v.id, e.name || ' — ' || s.name || ' (' || COALESCE(v.title, '') || ')' 
            FROM vacancies v
            JOIN enterprises e ON v.enterprise_id = e.id
            JOIN specialties s ON v.specialty_id = s.id
            WHERE v.is_active = TRUE
            ORDER BY e.name
        """
        return self.execute_query(query)

    def get_matching_candidates(self, v_id):
        """Возвращает список подходящих безработных для конкретной вакансии с баллами"""
        
        # 1. Получаем данные самой вакансии и её желательные навыки
        v_data = self.execute_query(
            "SELECT min_experience_years, gender, min_age, max_age, salary_min, salary_max FROM vacancies WHERE id = %s", 
            (v_id,)
        )[0]
        v_min_exp, v_gender, v_min_age, v_max_age, v_sal_min, v_sal_max = v_data

        # Получаем желательные навыки вакансии
        v_desired_skills_rows = self.execute_query(
            "SELECT skill_id FROM vacancy_skills WHERE vacancy_id = %s AND is_required = FALSE", 
            (v_id,)
        )
        v_desired_skills = set(row[0] for row in v_desired_skills_rows)

        # 2. SQL-запрос с ЖЕСТКИМИ фильтрами (специальность, образование, обязательные навыки)
        query = """
            SELECT 
                u.id, u.full_name, u.gender, EXTRACT(YEAR FROM AGE(u.birth_date)) AS age,
                u.experience_years, u.expected_salary, u.phone, u.email
            FROM unemployed u
            JOIN vacancies v ON v.id = %s
            LEFT JOIN education_levels ue ON u.education_level_id = ue.id
            LEFT JOIN education_levels ve ON v.education_level_id = ve.id
            WHERE v.specialty_id = u.specialty_id
              AND (ve.rank IS NULL OR ue.rank >= ve.rank)
              AND NOT EXISTS (
                  SELECT 1 FROM vacancy_skills vs
                  WHERE vs.vacancy_id = v.id AND vs.is_required = TRUE
                    AND vs.skill_id NOT IN (SELECT skill_id FROM unemployed_skills WHERE unemployed_id = u.id)
              )
        """
        candidates = self.execute_query(query, (v_id,))
        
        results = []
        for u in candidates:
            u_id, full_name, u_gender, u_age, u_exp, u_expected_salary, phone, email = u
            u_age = int(u_age) if u_age else 0
            u_exp = u_exp or 0
            
            # Получаем навыки кандидата для расчета желательных
            u_skills_rows = self.execute_query("SELECT skill_id FROM unemployed_skills WHERE unemployed_id = %s", (u_id,))
            u_skills = set(row[0] for row in u_skills_rows)

            # 3. Рассчитываем балл (от 0 до 100)
            score = 50 # Базовый балл
            
            # Стаж (макс +20)
            if not v_min_exp or u_exp >= v_min_exp:
                score += 20
            elif v_min_exp > 0:
                score += int((u_exp / v_min_exp) * 20)
                
            # Возраст (макс +10)
            age_ok = True
            if v_min_age and u_age < v_min_age: age_ok = False
            if v_max_age and u_age > v_max_age: age_ok = False
            if age_ok: score += 10
            
            # Пол (макс +5)
            if not v_gender or v_gender == u_gender:
                score += 5
                
            # Зарплата (макс +15)
            if not u_expected_salary:
                score += 15 
            elif v_sal_max and v_sal_max >= u_expected_salary:
                score += 15
            elif v_sal_min and v_sal_min >= u_expected_salary:
                score += 10
                
            # Желательные навыки (макс +10)
            if v_desired_skills:
                matched = len(v_desired_skills.intersection(u_skills))
                score += min(10, int((matched / len(v_desired_skills)) * 10))
            else:
                score += 10
                
            score = min(100, score)

            if score >= 60:
                results.append((
                    score, u_id, full_name, 
                    f"{u_exp} лет", f"{u_expected_salary or 'Не указана'} руб.",
                    f"{phone or ''} / {email or ''}"
                ))
                
        results.sort(key=lambda x: x[0], reverse=True)
        return results