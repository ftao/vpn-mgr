def parse_ip_line(line):
    '''
    parse somethig like 
    10.10.10-20,10.10.10.200
    '''
    line = line.strip()
    result = []
    parts = line.split(',')
    for item in parts:
        if '-' in item:
            start, end = item.split('-', 1)
            end = '.'.join([start.rsplit('.', 1)[0], end])
            result.append((start, end))
        else:
            result.append(item)
    return result


def is_ip_in_range(ip, ip_range):
    '''
    >>> ip_range = ['10.10.0.13', '10.10.0.200']
    >>> is_ip_in_range('10.10.0.9', ip_range)
    False
    >>> is_ip_in_range('10.10.0.10', ip_range)
    False
    >>> is_ip_in_range('10.10.0.13', ip_range)
    True
    >>> is_ip_in_range('10.10.0.129', ip_range)
    True
    >>> is_ip_in_range('10.10.0.200', ip_range)
    True
    >>> is_ip_in_range('10.10.0.201', ip_range)
    False
    >>> is_ip_in_range('10.10.1.20', ip_range)
    True
    >>> is_ip_in_range('10.10.1.21', ip_range)
    False
    '''
 
    def ip2inttuple(ip):
        return tuple([int(x) for x in ip.split('.')])

    if (ip2inttuple(ip) >= ip2inttuple(ip_range[0]) 
	and ip2inttuple(ip) <= ip2inttuple(ip_range[1])):
	return True
    return False
