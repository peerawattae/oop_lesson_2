import csv, os

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

cities = []
with open(os.path.join(__location__, 'Cities.csv')) as f:
    rows = csv.DictReader(f)
    for r in rows:
        cities.append(dict(r))

countries = []
with open(os.path.join(__location__, 'Countries.csv')) as f:
    rows = csv.DictReader(f)
    for r in rows:
        countries.append(dict(r))

player = []
with open(os.path.join(__location__, 'Players.csv')) as f:
    rows = csv.DictReader(f)
    for r in rows:
        player.append(dict(r))

Teams = []
with open(os.path.join(__location__, 'Teams.csv')) as f:
    rows = csv.DictReader(f)
    for r in rows:
        Teams.append(dict(r))

titanic = []
with open(os.path.join(__location__, 'Titanic.csv')) as f:
    rows = csv.DictReader(f)
    for r in rows:
        titanic.append(dict(r))


class DB:
    def __init__(self):
        self.database = []

    def insert(self, table):
        self.database.append(table)

    def search(self, table_name):
        for table in self.database:
            if table.table_name == table_name:
                return table
        return None


import copy


class Table:
    def __init__(self, table_name, table):
        self.table_name = table_name
        self.table = table

    def join(self, other_table, common_key):
        joined_table = Table(self.table_name + '_joins_' + other_table.table_name, [])
        for item1 in self.table:
            for item2 in other_table.table:
                if item1[common_key] == item2[common_key]:
                    dict1 = copy.deepcopy(item1)
                    dict2 = copy.deepcopy(item2)
                    dict1.update(dict2)
                    joined_table.table.append(dict1)
        return joined_table

    def filter(self, condition):
        filtered_table = Table(self.table_name + '_filtered', [])
        for item1 in self.table:
            if condition(item1):
                filtered_table.table.append(item1)
        return filtered_table


    def __is_float(self, element):
        if element is None:
            return False
        try:
            float(element)
            return True
        except ValueError:
            return False

    def aggregate(self, function, aggregation_key):
        temps = []
        for item1 in self.table:
            if self.__is_float(item1[aggregation_key]):
                temps.append(float(item1[aggregation_key]))
            else:
                temps.append(item1[aggregation_key])
        return function(temps)

    def select(self, attributes_list):
        temps = []
        for item1 in self.table:
            dict_temp = {}
            for key in item1:
                if key in attributes_list:
                    dict_temp[key] = item1[key]
            temps.append(dict_temp)
        return temps

    def pivot_table(self, keys_to_pivot_list, keys_to_aggreagte_list, aggregate_func_list):
        unique_values_list = []
        for key_item in keys_to_pivot_list:
            temp = []
            for dict in self.table:
                if dict[key_item] not in temp:
                    temp.append(dict[key_item])
            unique_values_list.append(temp)
        # combination of unique value lists
        import combination_gen
        comb_list = combination_gen.gen_comb_list(unique_values_list)

        pivot_table = []
        # filter each combination
        for item in comb_list:
            temp_filter_table = self
            for i in range(len(item)):
                temp_filter_table = temp_filter_table.filter(lambda x: x[keys_to_pivot_list[i]] == item[i])

            # aggregate over the filtered table
            aggregate_val_list = []
            for i in range(len(keys_to_aggreagte_list)):
                aggregate_val = temp_filter_table.aggregate(aggregate_func_list[i], keys_to_aggreagte_list[i])
                aggregate_val_list.append(aggregate_val)
            pivot_table.append([item, aggregate_val_list])
        return pivot_table

    def __str__(self):
        return self.table_name + ':' + str(self.table)

    


table1 = Table('cities', cities)
table2 = Table('countries', countries)
table4 = Table('players', player)
table5 = Table('Teams', Teams)
table6 = Table('Titanic', titanic)
titanic_db = DB()
titanic_db.insert(table6)
my_DB = DB()
my_DB.insert(table1)
my_DB.insert(table2)
my_table1 = my_DB.search('cities')

print("Test filter: only filtering out cities in Italy")
my_table1_filtered = my_table1.filter(lambda x: x['country'] == 'Italy')
print(my_table1_filtered)
print()

print("Test select: only displaying two fields, city and latitude, for cities in Italy")
my_table1_selected = my_table1_filtered.select(['city', 'latitude'])
print(my_table1_selected)
print()

print("Calculting the average temperature without using aggregate for cities in Italy")
temps = []
for item in my_table1_filtered.table:
    temps.append(float(item['temperature']))
print(sum(temps) / len(temps))
print()

print("Calculting the average temperature using aggregate for cities in Italy")
print(my_table1_filtered.aggregate(lambda x: sum(x) / len(x), 'temperature'))
print()

print("Test join: finding cities in non-EU countries whose temperatures are below 5.0")
my_table2 = my_DB.search('countries')
my_table3 = my_table1.join(my_table2, 'country')
my_table3_filtered = my_table3.filter(lambda x: x['EU'] == 'no').filter(lambda x: float(x['temperature']) < 5.0)
print(my_table3_filtered.table)
print()
print("Selecting just three fields, city, country, and temperature")
print(my_table3_filtered.select(['city', 'country', 'temperature']))
print()

print("Print the min and max temperatures for cities in EU that do not have coastlines")
my_table3_filtered = my_table3.filter(lambda x: x['EU'] == 'yes').filter(lambda x: x['coastline'] == 'no')
print("Min temp:", my_table3_filtered.aggregate(lambda x: min(x), 'temperature'))
print("Max temp:", my_table3_filtered.aggregate(lambda x: max(x), 'temperature'))
print()

print("Print the min and max latitude for cities in every country")
for item in my_table2.table:
    my_table1_filtered = my_table1.filter(lambda x: x['country'] == item['country'])
    if len(my_table1_filtered.table) >= 1:
        print(item['country'], my_table1_filtered.aggregate(lambda x: min(x), 'latitude'),
              my_table1_filtered.aggregate(lambda x: max(x), 'latitude'))
print()

table4_filtered = table4.filter(lambda x: 'ia' in x['team']).filter(lambda x: int(x['minutes']) < 200).filter(lambda x: int(x['passes']) > 100)
print(
    f'player on a team with “ia” in the team name played less than 200 minutes and made more than 100 passes '
    f'is {table4_filtered}'
)
table5_filtered_high = table5.filter(lambda x: int(x['ranking']) <= 10).aggregate(lambda x: sum(x)/len(x), 'games')
table5_filtered_low = table5.filter(lambda x: int(x['ranking']) > 10).aggregate(lambda x: sum(x)/len(x), 'games')
print(
    f'average number of games played for teams ranking below 10 is {table5_filtered_low:.3f} '
    f'versus teams ranking above or equal 10 is {table5_filtered_high:.3f}'
)
table4_filtered_forward = table4.filter(lambda x: 'forward' in x['position']).aggregate(lambda x: sum(x)/len(x), 'passes')
table4_filtered_midfielder = table4.filter(lambda x: 'midfielder' in x['position']).aggregate(lambda x: sum(x)/len(x), 'passes')
print(f'average passes for forward is {table4_filtered_forward:.3f}average passes for midfielder is {table4_filtered_midfielder:.3f}')
table6_filtered_first = table6.filter(lambda x: '1' in x['class']).aggregate(lambda x: sum(x)/len(x), 'fare')
table6_filtered_third = table6.filter(lambda x: '3' in x['class']).aggregate(lambda x: sum(x)/len(x), 'fare')
print(
    f'prices in first class ticket is {table6_filtered_first:.3f}'
    f'prices in third class ticket is {table6_filtered_third:.3f}'
)
table6_filtered_male = table6.filter(lambda x: 'M' in x['gender']).aggregate(lambda x: len(x), 'fare')
table6_filtered_male_survived = table6.filter(lambda x: 'M' in x['gender']).filter(lambda x: 'yes' in x['survived']).aggregate(lambda x: len(x), 'fare')
table6_filtered_female = table6.filter(lambda x: 'F' in x['gender']).aggregate(lambda x: len(x), 'fare')
table6_filtered_female_survived = table6.filter(lambda x: 'F' in x['gender']).filter(lambda x: 'yes' in x['survived']).aggregate(lambda x: len(x), 'fare')
print(
    f'survival rate of male is {(table6_filtered_male_survived/table6_filtered_male)*100:.3f} and '
    f'survival rate of female is {(table6_filtered_female_survived/table6_filtered_female)*100:.3f}'
)
table6_filtered_southampton = table6.filter(lambda x: 'Southampton' in x['embarked']).aggregate(lambda x: len(x), 'fare')
print(
    f'number of people that embarked from Southampton is {table6_filtered_southampton}'
)