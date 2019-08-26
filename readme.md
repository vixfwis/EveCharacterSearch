# Eve Character Search

![preview](https://cloud.githubusercontent.com/assets/546891/17384760/d1005850-59a3-11e6-93e0-8efb915ef035.png)

Eve Character Search is at the front a dynamic webpage that allows searching a live database of eve online character sales from the Character Bazaar Forums, and a scraping tool that monitors the forums and scrapes detailed information on the character for sale into a database for the webpage.

ECS leverages [Django][django] and [BeautifulSoup][beautifulsoup].

## Getting Started

### Linux

Install `pipenv`

```shell
$ pip3 install pipenv
```

Install requirements

```shell
$ pipenv install
```

Get into virtual shell. Edit `environ` if necessary

```shell
$ pipenv shell
$ source environ
```

Prepare your local instance

```shell
$ python manage.py makemigrations
$ python manage.py migrate
$ python manage.py update_api
```

Scrape some bazaar threads

```shell
$ python manage.py scrape_threads --pages 5
```

Start a local instance of `EveCharacterSearch`.

```shell
python manage.py runserver
```

---

[MIT][mit] © [shughes-uk][author] et [al][contributors]

[mit]:              http://opensource.org/licenses/MIT
[author]:           http://github.com/shughes-uk
[contributors]:     https://github.com/shughes-uk/EveCharacterSearch/graphs/contributors
[django]:           https://github.com/django/django
[beautifulsoup]:    https://www.crummy.com/software/BeautifulSoup/
