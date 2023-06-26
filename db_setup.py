import sqlite3

DB_NAME = 'inventory.db'

TABLES = [
    ('users',[
        'username string PRIMARY KEY',
        'hash string NOT NULL'
        ]),
    ('visits',[
        'v_id integer PRIMARY KEY AUTOINCREMENT',
        'date string',
        'name string',
        ]),
    ('items',[
        'i_id integer PRIMARY KEY AUTOINCREMENT',
        'name string'
        ]),
    ('visit_items',[
        'v_id integer',
        'i_id integer',
        'qty integer'
        ]),
    ('transactions',[
        't_id integer PRIMARY KEY AUTOINCREMENT',
        'timestamp string'
        ]),
    ('transaction_items',[
        't_id integer',
        'i_id integer',
        'qty integer'
        ])
    ]

def build_tables():
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()

    for table in TABLES:
        cmd = 'CREATE TABLE IF NOT EXISTS {} ({})'.format(table[0],', '.join(table[1]))
        print(cmd)
        cur.execute(cmd)

        con.commit()
        con.close()


if __name__ == "__main__":
    build_tables()
