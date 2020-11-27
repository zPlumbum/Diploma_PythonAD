import sqlalchemy

DB_path = input('Укажите путь до базы данных: ')


class DbWorker:
    def __init__(self, db_path):
        self.db_path = db_path

    def create_db_tables(self):
        db = self.db_path
        engine = sqlalchemy.create_engine(db)
        connection = engine.connect()

        connection.execute('''CREATE table if not exists vk_user(id serial primary key, vk_id integer unique not null,
        first_name varchar(30) not null, second_name varchar(30), age integer check(age > 0), city varchar(30));''')

        connection.execute('''CREATE table if not exists pairs(id serial primary key, vk_id integer unique not null,
        first_name varchar(30) not null, second_name varchar(30), profile_url text not null);''')

        connection.execute('''CREATE table if not exists userpair(user_id integer references vk_user(vk_id),
        pair_id integer references pairs(vk_id), constraint pk primary key (user_id, pair_id));''')

        connection.execute('''CREATE table if not exists photos(id serial primary key,
        id_pair integer references pairs(vk_id) not null, photo_link text not null,
        count_likes integer check(count_likes >= 0) not null);''')

        connection.execute('''CREATE table if not exists blacklist(id serial primary key, vk_id integer not null,
        first_name varchar(30) not null, second_name varchar(30), profile_link text not null,
        user_id integer references vk_user(vk_id));''')

    def add_user_to_db(self, user_info_dict, age):
        try:
            db = self.db_path
            engine = sqlalchemy.create_engine(db)
            connection = engine.connect()

            user_id = user_info_dict['vk_id']
            duplicate_id = connection.execute(f'''SELECT vk_id FROM vk_user
            WHERE vk_id = {user_id};''').fetchall()

            if duplicate_id:
                print('Этот пользователь уже есть в базе данных')
            else:
                connection.execute(f'''INSERT INTO vk_user(vk_id, first_name, second_name, age, city)
                VALUES({user_id}, '{user_info_dict['first_name']}', '{user_info_dict['last_name']}', {age}, '{user_info_dict['city_title']}');''')
                print('Пользователь успешно добавлен в базу данных')

        except Exception as ex:
            print(ex)
            print('Ошибка при добавлении пользователя в базу данных')

    def add_liked_to_db(self, user_id, person):
        try:
            db = self.db_path
            engine = sqlalchemy.create_engine(db)
            connection = engine.connect()

            liked_user_id = person['user_id']
            duplicate_id = connection.execute(f'''SELECT vk_id FROM pairs
            WHERE vk_id = {liked_user_id};''').fetchall()

            if duplicate_id:
                print('Этот пользователь уже есть в базе данных')
            else:
                connection.execute(f'''INSERT INTO pairs(vk_id, first_name, second_name, profile_url)
                VALUES({liked_user_id}, '{person['first_name']}', '{person['last_name']}', '{person['url']}');''')
                self.add_photo_links_to_db(person)
                print('Пользователь успешно добавлен в базу данных')

            duplicate_user_pair = connection.execute(f'''SELECT user_id, pair_id FROM userpair
            WHERE user_id = {user_id} AND pair_id = {liked_user_id};''').fetchall()

            if duplicate_user_pair:
                print('Этот человек уже в списке понравившихся')
                return False
            else:
                connection.execute(f'''INSERT INTO userpair(user_id, pair_id)
                VALUES({user_id}, {liked_user_id});''')
                print('Человек добавлен в список понравившихся')
                return True

        except Exception as ex:
            print(ex)
            print('Ошибка при добавлении пользователя в понравившиеся')

    def add_photo_links_to_db(self, person):
        try:
            db = self.db_path
            engine = sqlalchemy.create_engine(db)
            connection = engine.connect()

            dating_user_id = person['user_id']

            for photo_id, count_likes, photo_link in person['profile_photos']:
                duplicate_id = connection.execute(f'''SELECT photo_link FROM photos
                WHERE photo_link = '{photo_link}';''').fetchall()

                if duplicate_id:
                    print('Это фото уже есть в базе данных')
                else:
                    connection.execute(f'''INSERT INTO photos(id_pair, photo_link, count_likes)
                    VALUES({dating_user_id}, '{photo_link}', {count_likes});''')
                    print('Фото успешно добавлено в базу данных')

        except Exception as ex:
            print(ex)
            print('Ошибка при добавлении фотографий пользователя в базу данных')

    def add_to_blacklist(self, user_id, person):
        try:
            db = self.db_path
            engine = sqlalchemy.create_engine(db)
            connection = engine.connect()

            vk_id = person['user_id']
            duplicate_id = connection.execute(f'''SELECT vk_id FROM blacklist
            WHERE vk_id = {vk_id};''').fetchall()

            if duplicate_id:
                print('Пользователь уже в черном списке')
            else:
                connection.execute(f'''INSERT INTO blacklist(vk_id, first_name, second_name, profile_link, user_id)
                VALUES({vk_id}, '{person['first_name']}', '{person['last_name']}', '{person['url']}', {user_id});''')

        except Exception as ex:
            print(ex)
            print('Ошибка при добавлении пользователяв чс')

    def delete_from_blacklist(self, user_id, person_id):
        try:
            db = self.db_path
            engine = sqlalchemy.create_engine(db)
            connection = engine.connect()

            duplicate_id = connection.execute(f'''SELECT vk_id FROM blacklist
            WHERE user_id = {user_id} AND vk_id = {person_id};''').fetchall()

            if duplicate_id:
                connection.execute(f'''DELETE FROM blacklist
                WHERE vk_id = {person_id};''')
                print('Пользователь успешно удален из черного списка')
                return True
            else:
                print('Пользователя с таким id нет в черном списке')
                return False

        except Exception as ex:
            print(ex)
            print('Ошибка при удалении пользователя из чс')

    def show_blacklist(self, user_id):
        try:
            db = self.db_path
            engine = sqlalchemy.create_engine(db)
            connection = engine.connect()

            blacklist = connection.execute(f'''SELECT vk_id, first_name, second_name, profile_link FROM blacklist
            WHERE user_id = {user_id}''').fetchall()

            blacklist_people = []
            for person in blacklist:
                blacklist_people.append(
                    {
                        'user_id': person[0],
                        'first_name': person[1],
                        'last_name': person[2],
                        'profile_url': person[3]
                    }
                )

            return blacklist_people

        except Exception as ex:
            print(ex)
            print('Ошибка при выводе людей из базы данных черного списка')

    def show_liked_people(self, user_id):
        try:
            db = self.db_path
            engine = sqlalchemy.create_engine(db)
            connection = engine.connect()

            liked_people = connection.execute(f'''SELECT pairs.vk_id, pairs.first_name, pairs.second_name, profile_url FROM pairs
            JOIN userpair ON pairs.vk_id = userpair.pair_id
            JOIN vk_user ON userpair.user_id = vk_user.vk_id
            WHERE vk_user.vk_id = {user_id}''').fetchall()

            liked_people_list = []
            for person in liked_people:
                liked_people_list.append(
                    {
                        'user_id': person[0],
                        'first_name': person[1],
                        'last_name': person[2],
                        'profile_url': person[3]
                    }
                )

            return liked_people_list

        except Exception as ex:
            print(ex)
            print('Ошибка при выводе понравившихся людей из базы данных')
