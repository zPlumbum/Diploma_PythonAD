import requests
import sqlalchemy
from random import randint
from pprint import pprint
from vk_config import token

DB_path = input('DB path: ')


class VkBot:
    def __init__(self, user_token):
        self.token = user_token
        self.vk_version = 5.126

    def find_pairs(self, age_from, age_to, sex, city, count=3, status=6):
        offset = randint(0, 1000-count)

        response = requests.get(
            'https://api.vk.com/method/users.search',
            params={
                'access_token': self.token,
                'sex': sex,
                'status': status,
                'age_from': age_from,
                'age_to': age_to,
                'city': city,
                'count': count,
                'fields': 'screen_name,city,is_closed',
                'offset': offset,
                'v': self.vk_version
            }
        )
        people = response.json()

        people_list = []
        for person in people['response']['items']:
            if not person['is_closed']:
                url = f'https://vk.com/{person["screen_name"]}'
                user_id = person['id']
                first_name = person['first_name']
                last_name = person['last_name']
                profile_photos = self.get_most_popular_photos(user_id)

                people_list.append(
                    {
                        'user_id': user_id,
                        'first_name': first_name,
                        'last_name': last_name,
                        'url': url,
                        'profile_photos': profile_photos
                    }
                )
        return people_list

    def get_most_popular_photos(self, user_id):
        response_photos = requests.get(
            'https://api.vk.com/method/photos.get',
            params={
                'access_token': self.token,
                'owner_id': user_id,
                'album_id': 'profile',
                'rev': 1,
                'extended': 1,
                'v': self.vk_version
            }
        )

        photos_list = []
        for photo in response_photos.json()['response']['items']:
            photo_url = 'photo' + str(photo['owner_id']) + '_' + str(photo['id'])
            likes_count = photo['likes']['count']
            photos_list.append((photo_url, likes_count))

        photos_list = sorted(photos_list, key=lambda x: x[1])

        if len(photos_list) > 3:
            return photos_list[-3:]
        else:
            return photos_list

    def get_user_info(self, user_id):
        response = requests.get(
            'https://api.vk.com/method/users.get',
            params={
                'access_token': self.token,
                'user_ids': user_id,
                'fields': 'city,sex',
                'v': self.vk_version
            }
        )
        user_info = response.json()['response'][0]
        city_title = None
        city_id = None
        if 'city' in user_info.keys():
            city_title = user_info['city']['title']
            city_id = user_info['city']['id']

        user_info_dict = {
            'vk_id': user_info['id'],
            'first_name': user_info['first_name'],
            'last_name': user_info['last_name'],
            'city_title': city_title,
            'city_id': city_id,
            'sex': user_info['sex']
        }
        return user_info_dict

    @staticmethod
    def add_user_to_db(user_info_dict, age, db_path=DB_path):
        db = db_path
        engine = sqlalchemy.create_engine(db)
        connection = engine.connect()

        user_id = user_info_dict['vk_id']
        duplicate_id = connection.execute(f'''SELECT vk_id FROM vk_user
        WHERE vk_id = {user_id};''').fetchall()

        print(duplicate_id)

        if duplicate_id:
            print('Этот пользователь уже есть в базе данных')
        else:
            connection.execute(f'''INSERT INTO vk_user(vk_id, first_name, second_name, age, city)
            VALUES({user_id}, '{user_info_dict['first_name']}', '{user_info_dict['last_name']}', {age}, '{user_info_dict['city']}');''')
            print('Пользователь успешно добавлен в базу данных')

    @staticmethod
    def add_liked_to_db(user_id, person, age, db_path=DB_path):
        db = db_path
        engine = sqlalchemy.create_engine(db)
        connection = engine.connect()

        liked_user_id = person['user_id']
        duplicate_id = connection.execute(f'''SELECT vk_id, id_vk_user FROM datinguser
        WHERE vk_id = {liked_user_id} AND id_vk_user = {user_id};''').fetchall()

        if duplicate_id:
            print('Этот пользователь уже есть в базе данных')
        else:
            connection.execute(f'''INSERT INTO datinguser(vk_id, first_name, second_name, age, id_vk_user)
            VALUES({liked_user_id}, '{person['first_name']}', '{person['last_name']}', {age}, {user_id});''')
            print('Пользователь успешно добавлен в базу данных')

    @staticmethod
    def add_photo_links_to_db(person, db_path=DB_path):
        db = db_path
        engine = sqlalchemy.create_engine(db)
        connection = engine.connect()

        dating_user_id = person['user_id']

        for photo_link, count_likes in person['profile_photos']:
            duplicate_id = connection.execute(f'''SELECT id_datinguser, link_photo FROM photos
            WHERE id_datinguser = {dating_user_id} AND link_photo = '{photo_link}';''').fetchall()

            if duplicate_id:
                print('Это фото уже есть в базе данных')
            else:
                connection.execute(f'''INSERT INTO photos(id_datinguser, link_photo, count_likes)
                VALUES({dating_user_id}, '{photo_link}', {count_likes});''')
                print('Фото успешно добавлено в базу данных')

    @staticmethod
    def add_to_blacklist(person, db_path=DB_path):
        db = db_path
        engine = sqlalchemy.create_engine(db)
        connection = engine.connect()

        user_id = person['user_id']
        duplicate_id = connection.execute(f'''SELECT vk_id FROM blacklist
        WHERE vk_id = {user_id};''').fetchall()

        if duplicate_id:
            print('Пользователь уже есть базе данных')
        else:
            connection.execute(f'''INSERT INTO blacklist(vk_id, first_name, second_name)
            VALUES({user_id}, '{person['first_name']}', '{person['last_name']}');''')

    @staticmethod
    def delete_from_blacklist(person, db_path=DB_path):
        db = db_path
        engine = sqlalchemy.create_engine(db)
        connection = engine.connect()

        user_id = person['user_id']
        duplicate_id = connection.execute(f'''SELECT vk_id FROM blacklist
        WHERE vk_id = {user_id};''').fetchall()

        if duplicate_id:
            connection.execute(f'''DELETE FROM blacklist
            WHERE vk_id = {user_id};''')
            print('Пользователь успешно удален из черного списка')
        else:
            print('Пользователя с таким id нет в черном списке')

    @staticmethod
    def show_liked_people(user_id, db_path=DB_path):
        db = db_path
        engine = sqlalchemy.create_engine(db)
        connection = engine.connect()

        liked_people = connection.execute(f'''SELECT vk_id, first_name, second_name, age FROM datinguser
        WHERE id_vk_user = {user_id}''').fetchall()

        liked_people_list = []
        for person in liked_people:
            liked_people_list.append(
                {
                    'user_id': person[0],
                    'first_name': person[1],
                    'last_name': person[2],
                    'age': person[3]
                }
            )

        return liked_people_list


if __name__ == '__main__':
    vk_bot = VkBot(token)
