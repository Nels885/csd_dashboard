def derive_precode(precode):
    if not len(precode):
        # raise ValueError("Could not compute the code with a empty precode !")
        return None

    precode = precode.upper()

    x = ord(precode[1]) + (ord(precode[0]) * 5 * 2 - 698)
    y = ord(precode[3]) + (ord(precode[2]) * 5 * 2 + x) - 0x210
    z = ((y << 3) - y) % 100

    computed_code = (z // 10) + (z % 10) * 5 * 2 + ((0x103 % x) % 100) * 5 * 5 * 4
    computed_code = "%04d" % computed_code

    return computed_code
