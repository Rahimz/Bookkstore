def number_converter(input_phone):
    """
    This function get a number in 'fa' and changed it to 'en' numbers.
    """
    # converting dictionary
    conv_dict = {chr(48):chr(48), chr(49):chr(49), chr(50):chr(50), chr(51):chr(51), chr(52):chr(52), chr(53):chr(53), chr(54):chr(54),
                  chr(55):chr(55), chr(56):chr(56), chr(57):chr(57), chr(1632):chr(48), chr(1633):chr(49), chr(1634):chr(50),
                  chr(1635):chr(51), chr(1636):chr(52), chr(1637):chr(53), chr(1638):chr(54), chr(1639):chr(55), chr(1640):chr(56),
                  chr(1641):chr(57), chr(1776):chr(48), chr(1777):chr(49), chr(1778):chr(50), chr(1779):chr(51), chr(1780):chr(52),
                  chr(1781):chr(53), chr(1782):chr(54), chr(1783):chr(55), chr(1784):chr(56), chr(1785):chr(57)}

    # converting input string to string format
    if type(input_phone) == int or type(input_phone) == float:
        input_phone = str(input_phone)

    # converting input string
    res = ''
    for i in input_phone:
        if chr(ord(i)) in conv_dict:
            res += conv_dict.get(i, '')
        else:
            res += i

    # adding initial +
    # res = '+' + res

    return res
