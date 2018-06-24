import json
import sqlite3
import os


FILE_PATH = os.getcwd()
print(FILE_PATH)


def response(flow):
    request = flow.request
    responses = flow.response
    if request.url == 'http://xf.wh.cn/webApp/Handler/Subject.ashx':
        q_a = json.loads(responses.text)
        if 'result' in q_a.keys():
            add_answer(q_a)
        elif 'SubjectResult' in q_a.keys():
            q_a = find_answer(q_a)
            responses.text = json.dumps(q_a, ensure_ascii=False)


def add_answer(data):
    db = load_db()
    answers = data['result'][0]['hdjl']
    for i in answers:
        answer = db.execute('SELECT * from xf where id=?', (i['topicId'], )).fetchall()
        if len(answer) != 0:
            continue
        else:
            try:
                db.execute('insert into xf values (?,?)', (i['topicId'], i['correctContent']))
            except (sqlite3.OperationalError, sqlite3.IntegrityError) as e:
                print('Could not complete operation：', e)
    db.commit()
    db.close()


def find_answer(data):
    db = load_db()
    for q in data['SubjectResult']:
        answer = db.execute('select answer from xf where id=?', (q['Id'], )).fetchall()
        if len(answer) != 0:
            if len(answer[0]) == 1:
                answer = answer[0][0]
                for k, v in q.items():
                    if v == answer:
                        q[k] = f'(正确){answer}'
    db.close()
    return data


def load_db():
    conn = sqlite3.connect(f'{FILE_PATH}/xf.db')
    return conn
