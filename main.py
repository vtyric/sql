import sqlite3
import pandas as pd
import re


def main():
    ## создание таблицы works
    con = sqlite3.connect('works.sqlite')
    cursor = con.cursor()
    cursor.execute('DROP TABLE if EXISTS works')
    cursor.execute(
        'CREATE TABLE if NOT EXISTS works (ID INTEGER PRIMARY KEY AUTOINCREMENT, salary INTEGER, educationType TEXT,'
        'jobTitle TEXT, qualification TEXT, gender TEXT, dateModify TEXT,skills TEXT,otherInfo TEXT)')
    print(cursor.execute('pragma table_info(works)').fetchall())
    print()

    ## добавление данных в works
    df = pd.read_csv("works.csv")
    df.to_sql("works", con, if_exists='append', index=False)
    print(cursor.execute('SELECT * FROM works limit 3').fetchall())
    print()

    ## создание таблицы гендера
    cursor.execute("CREATE TABLE if NOT EXISTS genders (ID INTEGER PRIMARY KEY AUTOINCREMENT, gender TEXT)")
    cursor.execute('INSERT INTO genders(gender) SELECT DISTINCT gender FROM works WHERE gender IS NOT NULL')
    print(cursor.execute('pragma table_info(genders)').fetchall())
    print(cursor.execute("SELECT * FROM genders").fetchall())
    print()

    ## связь гендера и воркс через гендер_id
    cursor.execute('ALTER TABLE works ADD COLUMN gender_id INTEGER REFERENCES genders(ID)')
    cursor.execute('UPDATE works SET gender_id = (SELECT ID FROM genders WHERE gender = works.gender)')
    cursor.execute('ALTER TABLE works DROP COLUMN gender')
    print(cursor.execute("pragma table_info(works)").fetchall())
    print(cursor.execute('SELECT gender_id FROM works limit 5').fetchall())
    print()

    ## аналогичные операции с таблицей образования(создать таблицу образования, связать ее по educ_id)
    cursor.execute("CREATE TABLE if NOT EXISTS education (ID INTEGER PRIMARY KEY AUTOINCREMENT, educationType TEXT)")
    cursor.execute(
        'INSERT INTO education(educationType) SELECT DISTINCT educationType FROM works WHERE educationType IS NOT NULL')
    cursor.execute('ALTER TABLE works ADD COLUMN educ_id INTEGER REFERENCES education(ID)')
    cursor.execute('UPDATE works SET educ_id = (SELECT ID FROM education WHERE educationType = works.educationType)')
    cursor.execute('ALTER TABLE works DROP COLUMN educationType')
    print(cursor.execute("pragma table_info(works)").fetchall())
    print(cursor.execute("SELECT * FROM education").fetchall())
    print(cursor.execute('SELECT educ_id FROM works limit 5').fetchall())
    print()

    ## очистить поля от HTML
    clear_data = []
    for id, skills, other_info in cursor.execute("SELECT ID, skills, otherInfo FROM works").fetchall():
        clear_data.append(get_clear_data(skills, other_info, id))
    cursor.executemany("UPDATE works SET skills = ?, otherInfo = ? WHERE ID = ?", clear_data)
    print(cursor.execute("SELECT * FROM works limit 3").fetchall())


def get_clear_data(skills, other_info, id):
    if skills is not None:
        skills = get_data_without_html_code(skills)
    if other_info is not None:
        other_info = get_data_without_html_code(other_info)
    return skills, other_info, id


def get_data_without_html_code(data):
    # замена лишних символов на пробел(иначе могут сливаться слова)
    data = re.sub(r'<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});', ' ', data)
    # замена подряд идущих пробелов на один
    data = re.sub(r'[  ]+', ' ', data)

    return data.strip()


if __name__ == "__main__":
    main()
