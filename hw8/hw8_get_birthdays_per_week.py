from datetime import datetime, timedelta


def get_birthdays_per_week(users):

    today = datetime.now()

    range_start = 5 - today.weekday()
    
    # Формируем список год-месяц-день для выходных на этой неделе и будней на следующей неделе
    ymd_list = [[(today + timedelta(days=delta)).year,
                 (today + timedelta(days=delta)).month,
                 (today + timedelta(days=delta)).day] for delta in range(range_start, range_start+7)]

    week_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Monday', 'Monday']
    week_birthdays = {'Monday': [], 'Tuesday': [], 'Wednesday': [], 'Thursday': [], 'Friday': []}
    for user in users:
        for ymd in ymd_list:
            if [user['birthday'].month, user['birthday'].day] == [ymd[1], ymd[2]]:
                # Если ДР выпадает на учетный месяц-день, ...
                week_birthdays[week_days[datetime(ymd[0], ymd[1], ymd[2]).weekday()]].append(user['name'])
                break

    for key, value in week_birthdays.items():
        if value != []:
            print(f'{key}: {", ".join(value)}')


get_birthdays_per_week([{'name': 'Jacob', 'birthday': datetime(year=1996, month=2, day=12)},
                        {'name': 'Logan', 'birthday': datetime(year=1988, month=2, day=12)},
                        {'name': 'Matthew', 'birthday': datetime(year=1977, month=2, day=12)},
                        {'name': 'Jackson', 'birthday': datetime(year=2000, month=2, day=13)},
                        {'name': 'Levi', 'birthday': datetime(year=1996, month=2, day=13)},
                        {'name': 'Mateo', 'birthday': datetime(year=1985, month=2, day=14)},
                        {'name': 'Theodore', 'birthday': datetime(year=1978, month=2, day=16)},
                        {'name': 'Aiden', 'birthday': datetime(year=1979, month=2, day=16)},
                        {'name': 'Samuel', 'birthday': datetime(year=1998, month=2, day=17)},
                        {'name': 'Joseph', 'birthday': datetime(year=2000, month=2, day=17)},
                        {'name': 'Aiden', 'birthday': datetime(year=1979, month=2, day=18)},
                        {'name': 'William', 'birthday': datetime(year=2001, month=2, day=19)},
                        {'name': 'James', 'birthday': datetime(year=1979, month=2, day=20)},
                        {'name': 'John', 'birthday': datetime(year=1988, month=2, day=21)},
                        {'name': 'Benjamin', 'birthday': datetime(year=1982, month=2, day=22)},
                        {'name': 'Lucas', 'birthday': datetime(year=1992, month=2, day=23)},
                        {'name': 'Mason', 'birthday': datetime(year=1995, month=2, day=24)},
                        {'name': 'Michael', 'birthday': datetime(year=1983, month=2, day=25)},
                        {'name': 'David', 'birthday': datetime(year=2000, month=2, day=26)},
                        {'name': 'Ethan', 'birthday': datetime(year=1995, month=2, day=27)},
                        {'name': 'Daniel', 'birthday': datetime(year=1993, month=2, day=28)}])
