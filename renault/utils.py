def derive_precode(precode):
    """
    Source code: https://lucasg.github.io/2019/08/03/Compute-renault-radio-code/
    """
    if not len(precode) == 4:
        return {'result': 'ERROR', 'message': 'Could not compute the code with a empty precode !'}

    precode = precode.upper()

    x = ord(precode[1]) + (ord(precode[0]) * 5 * 2 - 698)
    y = ord(precode[3]) + (ord(precode[2]) * 5 * 2 + x) - 0x210
    z = ((y << 3) - y) % 100

    computed_code = (z // 10) + (z % 10) * 5 * 2 + ((0x103 % x) % 100) * 5 * 5 * 4
    computed_code = "%04d" % computed_code

    return {'result': 'OK', 'code': computed_code}
