<!---Пример кода-->
[![Typing SVG](https://readme-typing-svg.herokuapp.com?color=%d9eb0f&lines=Управление+замерами)](https://git.io/typing-svg)
# UZM_excel


Управление замерами - это web-приложение на Django для генерации отчетов, хранения данных и работы с ними.  
<h2> Установка, настройка и запуск проекта </h3>

<h3> Установка </h3>  
<h4><b>1. Устанавливаем Python </b></h4> 
(Официальный сайт: https://www.python.org/downloads/windows/)    
<br/>Устанавливаем любую версию Python 3 старше 3.8    
<br/>
<h4><b>2. Клонируем репозиторий </b></h4>
<image src="https://user-images.githubusercontent.com/79474789/235148752-3631ffa7-706b-413a-9227-e5cbd2853cf2.png" alt="Файлы репозитория">
<br/>
<b>3. Открываем консоль с адресной строки проводника </b>  
<image src="https://user-images.githubusercontent.com/79474789/235149056-96bf3d1c-7892-41d2-bd52-6fdaab85b71e.png">
<image src="https://user-images.githubusercontent.com/79474789/235149078-20b69f43-f89b-43fd-8016-4d70562e14f9.png">
<br/>
<h4><b>4. Проверяем наличие Python и PIP </b></h4>
Прописываем команды:   
<br/>> python --version  
<br/>> pip --version  
<br/>Если версия pip не выводится: 
<br/>(https://pythonru.com/baza-znanij/ustanovka-pip-dlja-python-i-bazovye-komandy).  
<br/>Успешная проверка:
<image src="https://user-images.githubusercontent.com/79474789/235150465-ba2ebfae-dc96-43f6-ba28-9d07098327a9.png">
<br/>
<h4><b>5. Создаем и активируем виртуальное окружение </b>  </h4>
> python -m venv env   
<br/>> env\Scripts\activate 
<image src="https://user-images.githubusercontent.com/79474789/235152459-60821dd4-c0dd-4dd1-99f0-457258d3c7ad.png">
<br/>
<h4><b>6. Установка библиотек </b>  </h4>
> pip install -r requerments.txt  
<br/>Проверка установки библиотек:  
<br/>> pip list
<image src="https://user-images.githubusercontent.com/79474789/235153388-dd2b0970-604b-41c9-8c01-6471d642f6d7.png">
<br/>Если каких-то бибилотек нет в requirments.txt, для их установки используем:  
<br/>> pip install <название библиотеки>  
<br/>
<h4><b>7. Запуск проекта </b> </h4> 
Для запуска на локальном устройстве:  
<br/>> python manage.py runserver   
<br/>Успешный запуск проекта:
<image src="https://user-images.githubusercontent.com/79474789/235154129-0846adac-7f23-401d-b8f9-6c953eee95d1.png">
<image src="https://user-images.githubusercontent.com/79474789/235154229-24506897-d013-44ba-ace5-0c20d46363cb.png">

<br/>

UZM_excel.bat - файл для запуска проекта
