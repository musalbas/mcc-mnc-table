import fileinput

networks = []
countries = []

print '    private int[][] mcc_mnc = {'

for line in fileinput.input():
    row = line.strip().split(',')

    if row[4] not in countries:
        countries.append(row[4])

    if row[7] not in networks:
        networks.append(row[7])

    country = countries.index(row[4])
    network = networks.index(row[7])

    print '        {' + str(row[1]) + ', ' + str(row[3]) + ', ' + str(country) + ', ' + str(network) + '},'

print '    };'

def print_list(l, name):
    print '    private ' + name + '[] = {'

    for i in l:
        print '        "' + i + '",'

    print '    }'

print_list(countries, 'countries')
print_list(networks, 'networks')
