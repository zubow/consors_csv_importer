from consors import Depot, Database, colored
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def analyze_type_per_category_all_depots(cs_depots, label=None):
    for cs in cs_depots:
        cust_label = label + ' / ' + cs.depot_owner
        analyze_type_per_category(cs, label=cust_label)


def analyze_relative_performance_all_depots(cs_depots, label=None):
    for cs in cs_depots:
        cust_label = label + ' / ' + cs.depot_owner
        analyze_relative_performance(cs, label=cust_label)


def group_by_wkn_all_depots(cs_depots, label=None):
    amount_per_wkn = {}
    for cs in cs_depots:
        for so in cs.stocks:
            if so.WKN in amount_per_wkn:
                amount_per_wkn[so.WKN] += so.amount
            else:
                amount_per_wkn[so.WKN] = so.amount

    print('*** shares per WKN ***')
    print(amount_per_wkn)


def analyze_total_value(cs_depots, label=None):
    total_value = 0
    for cs in cs_depots:
        total_value += cs.depot_value

    print('**********************')
    print(colored(0, 255, 0, 'Total value of all depots: %.0f €' % (total_value)))
    print('**********************')


def analyze_type_per_category(cs, label=None):
    # analyze type of positions
    value_per_category = {'Zertifikat': 0, 'ETF': 0, 'Aktie': 0}
    for so in cs.stocks:
        value_per_category[so.type] += so.total_val_eur

    print('*** ***')
    print(value_per_category)

    sns.barplot(list(value_per_category.keys()), list(value_per_category.values()))
    plt.ylabel('Total value [EUR]')

    t_str = 'Total value per category'
    if label is not None:
        t_str += ' (' + label + ')'
    plt.title(t_str)
    plt.grid()
    plt.show()


def analyze_relative_performance(cs, label=None):
    # analyze rel perf
    v_rel_perf = []
    for so in cs.stocks:
        v = so.rel_perf
        if v is not None:
            v_rel_perf.append(v)

    y = np.asarray(v_rel_perf)
    sns.distplot(y)
    plt.ylabel('Density')
    plt.xlabel('Relative performance [%]')

    t_str = 'Distribution of relative performance'
    if label is not None:
        t_str += ' (' + label + ')'

    plt.title(t_str)
    plt.show()


def show_top_by_rel_perf(depot, top=True, label=None, M=10):
    # analyze rel perf
    v_WKN = []
    v_name = []
    v_rel_perf = []
    for so in depot.stocks:
        v = so.rel_perf
        if v is not None:
            if so.WKN not in v_WKN:
                # add only once
                v_name.append(so.get_short_name())
                v_WKN.append(so.WKN)
                v_rel_perf.append(v)

    idx = np.argsort(v_rel_perf)
    if top:
        best_indices = idx[::-1][:M]
    else:
        best_indices = idx[0:M]

    x = [v_name[bi] for bi in best_indices]
    y = [v_rel_perf[bi] for bi in best_indices]

    sns.barplot(y, x)
    plt.xlabel('Rel. performance [%s]')

    if top:
        t_str = 'Top ' + str(M) + ' positions'
    else:
        t_str = 'Flop ' + str(M) + ' positions'

    if label is not None:
        t_str += ' (' + label + ')'

    plt.title(t_str)
    plt.tight_layout()
    plt.show()


def compare_depots(cs_depots, label=None):

    # if multiple depots
    if len(cs_depots) > 1:
        depot_labels = []
        depot_values = []
        for cs in cs_depots:
            depot_labels.append(cs.depot_owner)
            depot_values.append(cs.depot_value)

        # print all depot values
        fig1, ax1 = plt.subplots()
        ax1.pie(depot_values, labels=depot_labels, autopct='%1.1f%%',
                shadow=True, startangle=90)
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

        t_str = 'Relative size of each depot'
        if label is not None:
            t_str += ' (' + label + ')'

        ax1.set_title(t_str)
        plt.show()

        sns.barplot(depot_labels, depot_values)
        plt.ylabel('Total value [EUR]')

        t_str = 'Absolute value of each depot'
        if label is not None:
            t_str += ' (' + label + ')'
        plt.title(t_str)
        plt.grid()

        plt.show()
    else:
        print('You need more than one depot')


def show_top_flops_all_depots(cs_depots, label=None):
    for cs in cs_depots:
        cust_label = label + ' / ' + cs.depot_owner
        show_top_by_rel_perf(cs, top=False, label=cust_label)
        show_top_by_rel_perf(cs, top=True, label=cust_label)


def analyze_from_database():
    db = Database()
    db.load_all_data()
    db.close()


# run
if __name__ == "__main__":

    analyze_from_database()