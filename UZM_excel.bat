mkdir files\Report_input
mkdir files\Report_out
python -m venv venv
call venv\Scripts\activate.bat
pip install -r requirements.txt
python manage.py runserver 10.23.125.145:9680