import os
from analyze_depot import *
from consors import Depot, Database, colored

import argparse

def load_depot_from_file(dir):
    cs_depots = []

    for filename in os.listdir(dir):
        qFileName = os.path.join(dir, filename)
        cs = Depot()
        cs.parse(qFileName)
        cs.print()
        cs_depots.append(cs)

    return cs_depots


# run
if __name__ == "__main__":
    # Usage: python import_newdata.py --label "4. Sept. 2021" "./data/04092021/"
    parser = argparse.ArgumentParser(description='Parsing CSV files exported from Consors')
    # Required positional argument
    parser.add_argument('dir', type=str,
                        help='The folder with the CSV files')
    parser.add_argument('--label', type=str,
                        help='The label to be used for plots')

    args = parser.parse_args()

    print("Argument values:")
    print(args.dir)
    print(args.label)

    sns.set_style('darkgrid')

    cs_depots = load_depot_from_file(args.dir)

    # store in DB
    db = Database()
    db.store_all_depots(cs_depots)
    db.close()

    compare_depots(cs_depots, label=args.label)
    show_top_flops_all_depots(cs_depots, label=args.label)
    analyze_type_per_category_all_depots(cs_depots, label=args.label)
    analyze_relative_performance_all_depots(cs_depots, label=args.label)

    # to export to my app
    group_by_wkn_all_depots(cs_depots, label=args.label)

    analyze_total_value(cs_depots, label=args.label)

