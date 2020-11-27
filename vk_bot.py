import requests
import time
from random import randint


class VkBot:
    def __init__(self, user_token):
        self.token = user_token
        self.vk_version = 5.126

    def find_pairs(self, age_from, age_to, sex, city, count=5, status=6):
        try:
            response_for_offset = requests.get(
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
                    'v': self.vk_version
                }
            )

            results_count = response_for_offset.json()['response']['count']

            if results_count < 1000:
                offset = randint(0, results_count-count)
            else:
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

        except Exception as ex:
            print(ex)
            print('Ошибка в метода поиска пар')

    def get_most_popular_photos(self, user_id):
        try:
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
            try:
                for photo in response_photos.json()['response']['items']:
                    photo_id = 'photo' + str(photo['owner_id']) + '_' + str(photo['id'])
                    photo_url = photo['sizes'][-1]['url']
                    likes_count = photo['likes']['count']
                    photos_list.append((photo_id, likes_count, photo_url))
                    time.sleep(0.05)
            except Exception as ex:
                print(ex)
                print('Произошла ошибка в работе с фотографиями')

            photos_list = sorted(photos_list, key=lambda x: x[1])

            if len(photos_list) > 3:
                return photos_list[-3:]
            else:
                return photos_list

        except Exception as ex:
            print(ex)
            print('Ошибка при поиске самых популярных фото')

    def get_user_info(self, user_id):
        try:
            response = requests.get(
                'https://api.vk.com/method/users.get',
                params={
                    'access_token': self.token,
                    'user_ids': user_id,
                    'fields': 'city,sex,screen_name',
                    'v': self.vk_version
                }
            )
            user_info = response.json()['response'][0]

            profile_url = f'https://vk.com/{user_info["screen_name"]}'
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
                'sex': user_info['sex'],
                'profile_url': profile_url
            }
            return user_info_dict

        except Exception as ex:
            print(ex)
            print('Ошибка в получении информации о пользователе')
