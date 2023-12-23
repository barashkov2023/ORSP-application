from django.shortcuts import render, redirect
from .models import City
from .forms import CityForm
import requests


def index(request):
    url = 'https://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&appid=271d1234d3f497eed5b1d80a07b3fcd1'

    err_msg = ''
    message = ''
    message_class = 'is-success'

    if request.method == 'POST':
        form = CityForm(request.POST)

        if form.is_valid():
            new_city = form.cleaned_data['name']

            try:
                r = requests.get(url.format(new_city)).json()

                if r['cod'] == 200:
                    existing_city_count = City.objects.filter(name=r['name']).count()

                    if existing_city_count == 0:
                        City.objects.create(name=r['name'])
                        message = 'Город успешно определён'

                    else:
                        err_msg = 'Город уже сохранён в базе данных'

                else:
                    err_msg = 'Город не найден'    

            except ConnectionError:
                err_msg = 'Не удалось получить данные'

    if err_msg:
        message = err_msg
        message_class = 'is-danger'

    form = CityForm()
    cities = City.objects.all()
    weather_data = []

    for city in cities:
        r = requests.get(url.format(city.name)).json()
        city_weather = {
            'city_name' : r['name'],
            'temperature' : r['main']['temp'],
            'description' : r['weather'][0]['description'],
            'icon' : r['weather'][0]['icon'],
        }
        weather_data.append(city_weather)

    context = {
        'weather_data' : weather_data,
        'form' : form,
        'message' : message,
        'message_class' : message_class
    }

    return render(request, 'weather/weather.html', context)


def delete(request, city_name):
    print(city_name)
    City.objects.get(name=city_name).delete()
    return redirect('home')
