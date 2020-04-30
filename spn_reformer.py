def reform(toponym_spn):
    a = abs(toponym_spn['lowerCorner'][0] - toponym_spn['upperCorner'][0])
    b = abs(toponym_spn['lowerCorner'][1] - toponym_spn['upperCorner'][1])
    return a, b
