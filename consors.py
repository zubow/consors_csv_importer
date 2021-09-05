import csv
import sqlite3

def float_de_to_en(value):
    if value == '':
        return None

    return float(value.replace(".", "").replace(",", "."))

def colored(r, g, b, text):
    return "\033[38;2;{};{};{}m{} \033[38;2;255;255;255m".format(r, g, b, text)

'''
    Information on each stock like name and type
'''
class Stock:
    def __init__(self, name, WKN, type, amount, buy_price_pl_tx, currency, total_val_eur, abs_perf, abs_perf_currency, rel_perf):
        self.name = name
        self.WKN = WKN
        self.type = type
        self.amount = amount
        self.buy_price_pl_tx = buy_price_pl_tx
        self.currency = currency
        self.total_val_eur = total_val_eur
        self.abs_perf = abs_perf
        self.abs_perf_currency = abs_perf_currency
        self.rel_perf = rel_perf

    def get_short_name(self, N=8):
        sname = (self.name[:N] + '..') if len(self.name) > N else self.name
        return sname

    def print(self):
        print('\tName: %s, WKN %s, type: %s, amount: %s, BUY: %s %s, total: %s EUR, perf (abs): %s %s, perf (rel): %s%%'
              % (self.name, self.WKN, self.type, self.amount, self.buy_price_pl_tx, self.currency, self.total_val_eur, self.abs_perf, self.abs_perf_currency, self.rel_perf))

'''
    A depot contains a set of stocks
'''
class Depot:

    def __init__(self):
        self.stocks = []

    def print(self):
        print('*** Depot ***')
        print('No.: %s' % self.depot_nr)
        print('Owner: %s' % self.depot_owner)
        print('Update: %s' % self.depot_ts)

        print('Value: %s€' % self.depot_value)
        print('Perf (abs): %s€' % self.depot_abs_perf)
        print('Perf (rel): %s%%' % self.depot_rel_perf)

        print('Positions: ')
        for s in self.stocks:
            s.print()

    def parse(self, qFileName):
        print('parsing ... %s' % qFileName)
        with open(qFileName, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=';')

            line = 1
            for row in reader:
                #print(row)
                if line == 2:
                    self.depot_nr = row[0]
                    self.depot_owner = row[1]
                    self.depot_ts = row[2]

                if line == 5:
                    self.depot_value = float_de_to_en(row[0])
                    self.depot_abs_perf = float_de_to_en(row[1])
                    self.depot_rel_perf = float_de_to_en(row[2])

                if line >= 8:
                    # check end
                    if row[0] == '':
                        break

                    # Name;WKN;Gattung;Stück/Nominal;Einstandskurs inkl. NK;Währung/Prozent;Einstandswert;Währung/Prozent;Veränderung Intraday;Kurs;Währung/Prozent;Datum/Zeit;
                    # Handelsplatz;Gesamtwert EUR;Entwicklung absolut;Währung/Prozent;Entwicklung prozentual
                    s = Stock(row[0], row[1], row[2], float_de_to_en(row[3]), float_de_to_en(row[4]), row[5], float_de_to_en(row[13]), float_de_to_en(row[14]), row[15], float_de_to_en(row[16]))
                    self.stocks.append(s)
                line += 1

'''
    Store everything inside two database tables
'''
class Database:

    def __init__(self):
        self.conn = sqlite3.connect('consors.db')


    def store_all_depots(self, cs_depots):
        for cs in cs_depots:
            self.store_new_snapshot(cs)
        print(colored(0, 255, 0, 'All new imported data stored in database'))

    def store_new_snapshot(self, depot):

        try:
            c = self.conn.cursor()

            # create table Depot
            c.execute('''CREATE TABLE IF NOT EXISTS Depot
                         (id integer PRIMARY KEY AUTOINCREMENT, nr int, owner text not null, ts timestamp, total_value real, abs_perf real, rel_perf real, UNIQUE (nr, ts))''')

            c.execute('''INSERT INTO Depot (nr, owner, ts, total_value, abs_perf, rel_perf)
                         VALUES(?, ?, ?, ?, ?, ?)''', (depot.depot_nr, depot.depot_owner, depot.depot_ts, depot.depot_value, depot.depot_abs_perf, depot.depot_rel_perf))

            depot_id = c.lastrowid
            print('ID: %d' % depot_id)

            # create table Stocks
            c.execute('''CREATE TABLE IF NOT EXISTS Stocks
                         (id integer PRIMARY KEY AUTOINCREMENT, name text not null, WKN int, type text, amount real, buy_price_pl_tx real, currency text, total_val_eur real, abs_perf real, abs_perf_currency real, rel_perf real,                       
                         depot_id integer not null, FOREIGN KEY (depot_id) REFERENCES Depot (id))''')

            for so in depot.stocks:
                c.execute('''INSERT INTO Stocks (name, WKN, type, amount, buy_price_pl_tx, currency, total_val_eur, abs_perf, abs_perf_currency, rel_perf, depot_id)
                             VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
                so.name, so.WKN, so.type, so.amount, so.buy_price_pl_tx, so.currency, so.total_val_eur, so.abs_perf, so.abs_perf_currency, so.rel_perf, depot_id))

            # commit the changes to db
            self.conn.commit()
        except sqlite3.IntegrityError:
            print(colored(255, 0, 0, 'Data already in the database; ignored'))
        except sqlite3.Error as err:
            print(colored(255, 0, 0, 'Error while inserting into db: %s' % err))
            raise err

    def load_all_data(self):

        cur = self.conn.cursor()
        cur.execute("SELECT * FROM Depot")

        rows = cur.fetchall()

        for row in rows:
            print(row)

        cur.execute("SELECT * FROM Stocks")

        rows = cur.fetchall()

        for row in rows:
            print(row)

    def close(self):
        self.conn.close()