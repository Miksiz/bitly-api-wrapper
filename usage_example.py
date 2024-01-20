import asyncio
from bitly_api import BitlyAPI
from exceptions import APIException
import os
from dotenv import load_dotenv, find_dotenv

# Загрузка переменных окружения
dotenv_file = find_dotenv()
load_dotenv(dotenv_file)
credentials = {
   'token': os.getenv("BITLY_TOKEN")
}

async def main():
  async with BitlyAPI(**credentials) as api:
    try:
      responses = await asyncio.gather(
          api.link.clicks(link='https://bit.ly/3S6yh0D'),
          api.link.clicks(link='47DgjIY'),
      )
    except APIException as err:
      print(err) # Для того, чтобы программа не ломалась, когда ссылки устаревшие
    else:
      for response in responses:
            print(response.link_clicks)  # output: <number of clicks>

    try:
        response = await api.link.clicks(link='bad_link_notfound')
    except APIException as err:
        print(err)  # output: [404] NOT FOUND

if __name__ == '__main__':
   asyncio.run(main())