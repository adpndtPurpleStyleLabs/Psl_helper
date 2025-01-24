from num2words import num2words

def convert_amount_to_words(amount):
    amount = float(amount)
    integer_part = int(amount)
    decimal_part = int(round((amount - integer_part) * 100))
    words = num2words(integer_part, lang='en_IN').replace(',', '').capitalize()
    if decimal_part > 0:
        words += f" and {num2words(decimal_part, lang='en_IN').replace(',', '').capitalize()} paise"

    return str(words + " only").upper()

def indexOfContainsInList(list, word):
    count = 0
    for alist in list:
        if str(alist).__contains__(word):
            return count
        count += 1
    return -1

def lastIndexOfContainsInList(list, word):
    newList = list[::-1]
    count = len(list)
    for alist in newList:
        if str(alist).__contains__(word):
            return count
        count -= 1
    return -1

def substring_before_second_occurrence(s, word):
    first_occurrence = s.find(word)
    if first_occurrence == -1:
        return s
    second_occurrence = s.find(word, first_occurrence + len(word))
    if second_occurrence == -1:
        return s[:first_occurrence]

    return s[:second_occurrence]

def substring_after_second_occurrence(s, word):
    first_occurrence = s.find(word)
    if first_occurrence == -1:
        return s
    second_occurrence = s.find(word, first_occurrence + len(word))
    if second_occurrence == -1:
        return s[:first_occurrence]

    return s[second_occurrence:]

def get_state_using_gst_id(code):
    mapping = {
        35: "ANDAMAN AND NICOBAR",
        37: "ANDHRA PRADESH",
        12: "ARUNACHAL PRADESH",
        18: "ASSAM",
        10: "BIHAR",
        4: "CHANDIGARH",
        22: "CHHATTISGARH",
        26: "DADAR AND NAGAR HAVELI",
        25: "DAMAN AND DIU",
        7: "NEW DELHI",
        30: "GOA",
        24: "GUJARAT",
        6: "HARYANA",
        2: "HIMACHAL PRADESH",
        1: "JAMMU AND KASHMIR",
        20: "JHARKHAND",
        29: "KARNATAKA",
        32: "KERALA",
        31: "LAKSHADWEEP",
        23: "MADHYA PRADESH",
        27: "MAHARASHTRA",
        14: "MANIPUR",
        17: "MEGHALAYA",
        15: "MIZORAM",
        13: "NAGALAND",
        21: "ODISHA",
        34: "PUDUCHERRY",
        3: "PUNJAB",
        8: "RAJASTHAN",
        11: "SIKKIM",
        33: "TAMIL NADU",
        36: "TELANGANA",
        16: "TRIPURA",
        9: "UTTAR PRADESH",
        5: "UTTARAKHAND",
        19: "WEST BENGAL",
        97: "OTHER TERRITORY",
        99: "OTHER COUNTRY"
    }
    state = "NA"
    try:
        state = mapping[code]
    except KeyError:
        print("Error while getting state for code {}".format(code))
    return state

def strip_array_before_specified_word(input_array, word):
    return input_array[indexOfContainsInList(input_array,word):]

def find_nth_occurrence_of(lst, word, n):
    count = 0
    for index, item in enumerate(lst):
        if item.__contains__(word):
            count += 1
            if count == n:
                return index
    return -1