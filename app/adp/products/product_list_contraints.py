
def width_slice(v1,v2):
    widths = [140,142,145,175,210,245,255]
    return widths[widths.index(v1):widths.index(v2)+1]

def width_slice_uc(v1,v2):
    widths = [130,140,155,170,200,205,235]
    return widths[widths.index(v1):widths.index(v2)+1]


constraints = {
    "series": {
        "slab_numbers": {
            "A": [10,11,12,14],
            "E": [21,22,30,31,32,"7J",33,"8J",34,"9J",35,"1K",36,"2K",48,84,
            20,23,24,25,26,27,37,"3K",47,49,50,51,52,53,54,55,72,74,80,81,82,83,86,88,91,92],
            "G": [21,22,30,31,32,"7J",33,"8J",34,"9J",35,"1K",36,"2K",48,84,
            20,23,24,25,26,27,37,"3K",47,49,50,51,52,53,54,55,72,74,80,81,82,83,86,88,91,92],
        }
    },
    "slab_numbers": {
        "tonnages": {
            11 :[36,42],
            12 :[36,42,48],
            14 :[42,48,60],
            20 :[18,24],
            23 :[24,30,36],
            24 :[24,30,36,42,48],
            25 :[42,48],
            26 :[48,60],
            27 :[48,60],
            37 :[36,42,48,60],
            "3K" :[48,60],
            47 :[36],
            49 :[48,60],
            50 :[48,60],
            51 :[42,48,60],
            52 :[48,60],
            53 :[36,42,48],
            54 :[48,60],
            55 :[48,60],
            72 :[60],
            74 :[60],
            80 :[36],
            81 :[36],
            82 :[36],
            83 :[36],
            86 :[48,60],
            88 :[48,60],
            91 :[18,24,30],
            92 :[24,30,36],
            10 :[36],
            21 :[18,24,30],
            22 :[18,24,30,36],
            30 :[18,24],
            31 :[18,24,30],
            32 :[24,30,36],
            "7J" :[24,30,36],
            33 :[30,36],
            "8J" :[30,36],
            34 :[36,42],
            "9J" :[30,36,42],
            35 :[36,42,48],
            "1K" :[36,42,48],
            36 :[36,42,48,60],
            "2K" :[48,60],
            48 :[36,42,48,60],
            84 :[42,48,60],
        },
        "heights": {
            "01": {
                11: 18,
                12: 20,
                14: 20,
                20: 12,
                23: 18,
                24: 20,
                25: 22,
                26: 25,
                27: 25,
                37: 25,
                "3K": 25,
                47: 31,
                49: 27,
                50: 27,
                51: 31,
                52: 31,
                53: 31,
                54: 31,
                55: 31,
                72: 25,
                74: 18,
                80: 20,
                81: 20,
                82: 25,
                83: 25,
                86: 27,
                88: 27,
                91: 16,
                92: 16,
                10: 16,
                21: 16,
                22: 16,
                30: 12,
                31: 16,
                32: 16,
                "7J": 16,
                33: 18,
                "8J": 18,
                34: 20,
                "9J": 20,
                35: 22,
                "1K": 22,
                36: 25,
                "2K": 25,
                48: 27,
                84: 25,
            },
            "05": {
                11: 18,
                12: 20,
                14: 20,
                20: 12,
                23: 18,
                24: 20,
                25: 22,
                26: 25,
                27: 25,
                37: 25,
                "3K": 25,
                47: 31,
                49: 27,
                50: 27,
                51: 31,
                52: 31,
                53: 31,
                54: 31,
                55: 31,
                72: 25,
                74: 18,
                80: 20,
                81: 20,
                82: 25,
                83: 25,
                86: 27,
                88: 27,
                91: 16,
                92: 16,
                10: 16,
                21: 16,
                22: 16,
                30: 12,
                31: 16,
                32: 16,
                "7J": 16,
                33: 18,
                "8J": 18,
                34: 20,
                "9J": 20,
                35: 22,
                "1K": 22,
                36: 25,
                "2K": 25,
                48: 27,
                84: 25,
            },
            "22": {
                11: 20,
                12: 20,
                14: 20,
                20: 16,
                23: 20,
                24: 20,
                25: 22,
                26: 25,
                27: 25,
                37: 25,
                "3K": 25,
                47: 31,
                49: 27,
                50: 27,
                51: 31,
                52: 0,
                53: 0,
                54: 31,
                55: 31,
                72: 0,
                74: 0,
                80: 20,
                81: 20,
                82: 25,
                83: 25,
                86: 27,
                88: 27,
                91: 16,
                92: 16,
                10: 16,
                21: 16,
                22: 16,
                30: 16,
                31: 16,
                32: 16,
                "7J": 16,
                33: 20,
                "8J": 20,
                34: 20,
                "9J": 20,
                35: 22,
                "1K": 22,
                36: 25,
                "2K": 25,
                48: 27,
                84: 25,
            },
            "20": {
                11: 20,
                12: 20,
                14: 20,
                20: 16,
                23: 20,
                24: 20,
                25: 22,
                26: 25,
                27: 25,
                37: 25,
                "3K": 25,
                47: 31,
                49: 27,
                50: 27,
                51: 31,
                52: 0,
                53: 0,
                54: 31,
                55: 31,
                72: 0,
                74: 0,
                80: 20,
                81: 20,
                82: 25,
                83: 25,
                86: 27,
                88: 27,
                91: 16,
                92: 16,
                10: 16,
                21: 16,
                22: 16,
                30: 16,
                31: 16,
                32: 16,
                "7J": 16,
                33: 20,
                "8J": 20,
                34: 20,
                "9J": 20,
                35: 22,
                "1K": 22,
                36: 25,
                "2K": 25,
                48: 27,
                84: 25,
            },
            "00": {
                11: 17,
                12: 19,
                14: 23,
                20: 11,
                23: 17,
                24: 19,
                25: 21,
                26: 23,
                27: 25,
                37: 25,
                "3K": 25,
                47: 27,
                49: 25,
                50: 27,
                51: 29,
                52: 31,
                53: 31,
                54: 29,
                55: 31,
                72: 23,
                74: 19,
                80: 17,
                81: 19,
                82: 21,
                83: 23,
                86: 25,
                88: 27,
                91: 13,
                92: 15,
                10: 15,
                21: 13,
                22: 15,
                30: 11,
                31: 13,
                32: 15,
                "7J": 15,
                33: 17,
                "8J": 17,
                34: 19,
                "9J": 19,
                35: 21,
                "1K": 21,
                36: 23,
                "2K": 23,
                48: 27,
                84: 23,
            },
            "04": {
                11: 17,
                12: 19,
                14: 23,
                20: 11,
                23: 17,
                24: 19,
                25: 21,
                26: 23,
                27: 25,
                37: 25,
                "3K": 25,
                47: 27,
                49: 25,
                50: 27,
                51: 29,
                52: 31,
                53: 31,
                54: 29,
                55: 31,
                72: 23,
                74: 19,
                80: 17,
                81: 19,
                82: 21,
                83: 23,
                86: 25,
                88: 27,
                91: 13,
                92: 15,
                10: 15,
                21: 13,
                22: 15,
                30: 11,
                31: 13,
                32: 15,
                "7J": 15,
                33: 17,
                "8J": 17,
                34: 19,
                "9J": 19,
                35: 21,
                "1K": 21,
                36: 23,
                "2K": 23,
                48: 27,
                84: 23,
            }
        },
        "widths": {
            "01": {
                11: {
                    36: width_slice(145,245),
                    42: width_slice(175,245)
                },
                12: {
                    36: width_slice(145,245),
                    42: width_slice(175,245),
                    48: width_slice(175,245),
                },
                14: {
                    42: width_slice(175,245),
                    48: width_slice(175,245),
                    60: width_slice(210,245)
                },
                20: {
                    18: width_slice(145,175),
                    24: width_slice(145,175)
                },
                23: {
                    24: width_slice(140,175),
                    30: width_slice(140,175),
                    36: width_slice(142,245)
                },
                24: {
                    24: width_slice(142,210),
                    30: width_slice(142,210),
                    36: width_slice(142,210),
                    42: width_slice(175,245),
                    48: width_slice(175,245),
                },
                25: {
                    42: width_slice(175,245),
                    48: width_slice(175,245)

                },
                26: {
                    48: width_slice(175,245),
                    60: width_slice(210,245)
                },
                27: {
                    48: width_slice(175,245),
                    60: width_slice(210,245)
                },
                37: {
                    36: width_slice(175,245),
                    42: width_slice(175,245),
                    48: width_slice(175,245),
                    60: width_slice(210,245)
                },
                "3K": {
                    48: width_slice(175,245),
                    60: width_slice(210,245)
                },
                47: {
                    36: width_slice(175,210)
                },
                49: {
                    48: width_slice(210,245),
                    60: width_slice(210,245)
                },
                50: {
                    48: width_slice(210,245),
                    60: width_slice(210,245),
                },
                51: {
                    42: width_slice(210,245),
                    48: width_slice(210,245),
                    60: width_slice(210,245),
                },
                52: {
                    48: width_slice(210,245),
                    60: width_slice(210,245),
                },
                53: {
                    36: width_slice(142,210),
                    42: width_slice(142,210),
                    48: width_slice(142,210),
                },
                54: {
                    48: width_slice(210,245),
                    60: width_slice(210,245),
                },
                55: {
                    48: width_slice(210,245),
                    60: width_slice(210,245),
                },
                72: {
                    60: [245]
                },
                74: {
                    60: [245]
                },
                80: {
                    36: width_slice(145,210)
                },
                81: {
                    36: width_slice(145,210)
                },
                82: {
                    36: width_slice(145,210)
                },
                83: {
                    36: width_slice(145,210)
                },
                86: {
                    48: width_slice(175,245),
                    60: width_slice(210,245)
                },
                88: {
                    48: width_slice(175,245),
                    60: width_slice(210,245)
                },
                91: {
                    18: width_slice(140,210),
                    24: width_slice(140,210),
                    30: width_slice(140,210)
                },
                92: {
                    24: width_slice(140,210),
                    30: width_slice(140,210),
                    36: width_slice(142,210)
                },
                10: {
                    36: width_slice(142,210),
                },
                21: {
                    18: width_slice(140,175),
                    24: width_slice(140,175),
                    30: width_slice(140,175)
                },
                22: {
                    18: width_slice(140,245),
                    24: width_slice(140,245),
                    30: width_slice(140,245),
                    36: width_slice(142,245)
                },
                30: {
                    18: width_slice(140,175),
                    24: width_slice(140,175)
                },
                31: {
                    18: width_slice(140,210),
                    24: width_slice(140,210),
                    30: width_slice(140,210)
                },
                32: {
                    24: width_slice(140,210),
                    30: width_slice(140,210),
                    36: width_slice(142,210)
                },
                "7J": {
                    24: width_slice(140,210),
                    30: width_slice(140,210),
                    36: width_slice(142,210)
                },
                33: {
                    30: width_slice(140, 245),
                    36: width_slice(142, 245)
                },
                "8J": {
                    30: width_slice(140, 245),
                    36: width_slice(142, 245)
                },
                34: {
                    36: width_slice(142, 245),
                    42: width_slice(175, 245)
                },
                "9J": {
                    30: width_slice(140, 245),
                    36: width_slice(142, 245),
                    42: width_slice(175, 245)
                },
                35: {
                    36: width_slice(142, 245),
                    42: width_slice(175, 245),
                    48: width_slice(175, 245)
                },
                "1K": {
                    36: width_slice(142, 245),
                    42: width_slice(175, 245),
                    48: width_slice(175, 245)
                },
                36: {
                    36: width_slice(142, 245),
                    42: width_slice(175, 245),
                    48: width_slice(175, 245),
                    60: width_slice(210, 245)
                },
                "2K": {
                    48: width_slice(175, 245),
                    60: width_slice(210, 245)
                },
                48: {
                    36: width_slice(175, 245),
                    42: width_slice(175, 245),
                    48: width_slice(175, 245),
                    60: width_slice(210, 245)
                },
                84: {
                    42: width_slice(175, 245),
                    48: width_slice(175, 245),
                    60: width_slice(210, 245)
                }
            },
            "05": {
                11: {
                    36: width_slice(145,245),
                    42: width_slice(175,245)
                },
                12: {
                    36: width_slice(145,245),
                    42: width_slice(175,245),
                    48: width_slice(175,245),
                },
                14: {
                    42: width_slice(175,245),
                    48: width_slice(175,245),
                    60: width_slice(210,245)
                },
                20: {
                    18: width_slice(145,175),
                    24: width_slice(145,175)
                },
                23: {
                    24: width_slice(140,175),
                    30: width_slice(140,175),
                    36: width_slice(142,245)
                },
                24: {
                    24: width_slice(142,210),
                    30: width_slice(142,210),
                    36: width_slice(142,210),
                    42: width_slice(175,245),
                    48: width_slice(175,245),
                },
                25: {
                    42: width_slice(175,245),
                    48: width_slice(175,245)

                },
                26: {
                    48: width_slice(175,245),
                    60: width_slice(210,245)
                },
                27: {
                    48: width_slice(175,245),
                    60: width_slice(210,245)
                },
                37: {
                    36: width_slice(175,245),
                    42: width_slice(175,245),
                    48: width_slice(175,245),
                    60: width_slice(210,245)
                },
                "3K": {
                    48: width_slice(175,245),
                    60: width_slice(210,245)
                },
                47: {
                    36: width_slice(175,210)
                },
                49: {
                    48: width_slice(210,245),
                    60: width_slice(210,245)
                },
                50: {
                    48: width_slice(210,245),
                    60: width_slice(210,245),
                },
                51: {
                    42: width_slice(210,245),
                    48: width_slice(210,245),
                    60: width_slice(210,245),
                },
                52: {
                    48: width_slice(210,245),
                    60: width_slice(210,245),
                },
                53: {
                    36: width_slice(142,210),
                    42: width_slice(142,210),
                    48: width_slice(142,210),
                },
                54: {
                    48: width_slice(210,245),
                    60: width_slice(210,245),
                },
                55: {
                    48: width_slice(210,245),
                    60: width_slice(210,245),
                },
                72: {
                    60: [245]
                },
                74: {
                    60: [245]
                },
                80: {
                    36: width_slice(145,210)
                },
                81: {
                    36: width_slice(145,210)
                },
                82: {
                    36: width_slice(145,210)
                },
                83: {
                    36: width_slice(145,210)
                },
                86: {
                    48: width_slice(175,245),
                    60: width_slice(210,245)
                },
                88: {
                    48: width_slice(175,245),
                    60: width_slice(210,245)
                },
                91: {
                    18: width_slice(140,210),
                    24: width_slice(140,210),
                    30: width_slice(140,210)
                },
                92: {
                    24: width_slice(140,210),
                    30: width_slice(140,210),
                    36: width_slice(142,210)
                },
                10: {
                    36: width_slice(142,210),
                },
                21: {
                    18: width_slice(140,175),
                    24: width_slice(140,175),
                    30: width_slice(140,175)
                },
                22: {
                    18: width_slice(140,245),
                    24: width_slice(140,245),
                    30: width_slice(140,245),
                    36: width_slice(142,245)
                },
                30: {
                    18: width_slice(140,175),
                    24: width_slice(140,175)
                },
                31: {
                    18: width_slice(140,210),
                    24: width_slice(140,210),
                    30: width_slice(140,210)
                },
                32: {
                    24: width_slice(140,210),
                    30: width_slice(140,210),
                    36: width_slice(142,210)
                },
                "7J": {
                    24: width_slice(140,210),
                    30: width_slice(140,210),
                    36: width_slice(142,210)
                },
                33: {
                    30: width_slice(140, 245),
                    36: width_slice(142, 245)
                },
                "8J": {
                    30: width_slice(140, 245),
                    36: width_slice(142, 245)
                },
                34: {
                    36: width_slice(142, 245),
                    42: width_slice(175, 245)
                },
                "9J": {
                    30: width_slice(140, 245),
                    36: width_slice(142, 245),
                    42: width_slice(175, 245)
                },
                35: {
                    36: width_slice(142, 245),
                    42: width_slice(175, 245),
                    48: width_slice(175, 245)
                },
                "1K": {
                    36: width_slice(142, 245),
                    42: width_slice(175, 245),
                    48: width_slice(175, 245)
                },
                36: {
                    36: width_slice(142, 245),
                    42: width_slice(175, 245),
                    48: width_slice(175, 245),
                    60: width_slice(210, 245)
                },
                "2K": {
                    48: width_slice(175, 245),
                    60: width_slice(210, 245)
                },
                48: {
                    36: width_slice(175, 245),
                    42: width_slice(175, 245),
                    48: width_slice(175, 245),
                    60: width_slice(210, 245)
                },
                84: {
                    42: width_slice(175, 245),
                    48: width_slice(175, 245),
                    60: width_slice(210, 245)
                }
            },
            "20": {
                11: {
                    36: width_slice(145,245),
                    42: width_slice(175,245)
                },
                12: {
                    36: width_slice(145,245),
                    42: width_slice(175,245),
                    48: width_slice(175,245),
                },
                14: {
                    42: width_slice(175,245),
                    48: width_slice(175,245),
                    60: width_slice(210,245)
                },
                20: {
                    18: width_slice(145,210),
                    24: width_slice(145,210)
                },
                23: {
                    24: width_slice(140,245),
                    30: width_slice(140,245),
                    36: width_slice(145,245)
                },
                24: {
                    24: width_slice(145,210),
                    30: width_slice(145,210),
                    36: width_slice(145,210),
                    42: width_slice(175,245),
                    48: width_slice(175,245),
                },
                25: {
                    42: width_slice(175,245),
                    48: width_slice(175,245)
                },
                26: {
                    48: width_slice(175,245),
                    60: width_slice(210,245)
                },
                27: {
                    48: width_slice(175,245),
                    60: width_slice(210,245)
                },
                37: {
                    36: width_slice(175,245),
                    42: width_slice(175,245),
                    48: width_slice(175,245),
                    60: width_slice(210,245)
                },
                "3K": {
                    48: width_slice(175,245),
                    60: width_slice(210,245)
                },
                47: {
                    36: width_slice(175,210)
                },
                49: {
                    48: width_slice(210,245),
                    60: width_slice(210,245)
                },
                50: {
                    48: width_slice(210,245),
                    60: width_slice(210,245),
                },
                51: {
                    42: width_slice(210,245),
                    48: width_slice(210,245),
                    60: width_slice(210,245),
                },
                52: {
                    48: [0],
                    60: [0],
                },
                53: {
                    36: [0],
                    42: [0],
                    48: [0],
                },
                54: {
                    48: width_slice(210,245),
                    60: width_slice(210,245),
                },
                55: {
                    48: width_slice(210,245),
                    60: width_slice(210,245),
                },
                72: {
                    60: [0]
                },
                74: {
                    60: [0]
                },
                80: {
                    36: width_slice(145,210)
                },
                81: {
                    36: width_slice(145,210)
                },
                82: {
                    36: width_slice(145,210)
                },
                83: {
                    36: width_slice(145,210)
                },
                86: {
                    48: width_slice(175,245),
                    60: width_slice(210,245)
                },
                88: {
                    48: width_slice(175,245),
                    60: width_slice(210,245)
                },
                91: {
                    18: width_slice(140,210),
                    24: width_slice(140,210),
                    30: width_slice(140,210)
                },
                92: {
                    24: width_slice(140,210),
                    30: width_slice(140,210),
                    36: width_slice(145,210)
                },
                10: {
                    36: width_slice(145,210),
                },
                21: {
                    18: width_slice(140,210),
                    24: width_slice(140,210),
                    30: width_slice(140,210)
                },
                22: {
                    18: width_slice(140,245),
                    24: width_slice(140,245),
                    30: width_slice(140,245),
                    36: width_slice(145,245)
                },
                30: {
                    18: width_slice(140,175),
                    24: width_slice(140,175)
                },
                31: {
                    18: width_slice(140,210),
                    24: width_slice(140,210),
                    30: width_slice(140,210)
                },
                32: {
                    24: width_slice(140,210),
                    30: width_slice(140,210),
                    36: width_slice(145,210)
                },
                "7J": {
                    24: width_slice(145,210),
                    30: width_slice(145,210),
                    36: width_slice(145,210)
                },
                33: {
                    30: width_slice(140, 245),
                    36: width_slice(142, 245)
                },
                "8J": {
                    30: width_slice(140, 245),
                    36: width_slice(145, 245)
                },
                34: {
                    36: width_slice(145, 245),
                    42: width_slice(175, 245)
                },
                "9J": {
                    30: width_slice(140, 245),
                    36: width_slice(145, 245),
                    42: width_slice(175, 245)
                },
                35: {
                    36: width_slice(145, 245),
                    42: width_slice(175, 245),
                    48: width_slice(175, 245)
                },
                "1K": {
                    36: width_slice(145, 245),
                    42: width_slice(175, 245),
                    48: width_slice(175, 245)
                },
                36: {
                    36: width_slice(145, 245),
                    42: width_slice(175, 245),
                    48: width_slice(175, 245),
                    60: width_slice(210, 245)
                },
                "2K": {
                    48: width_slice(175, 245),
                    60: width_slice(210, 245)
                },
                48: {
                    36: width_slice(175, 245),
                    42: width_slice(175, 245),
                    48: width_slice(175, 245),
                    60: width_slice(210, 245)
                },
                84: {
                    42: width_slice(175, 245),
                    48: width_slice(175, 245),
                    60: width_slice(210, 245)
                }
            },
            "22": {
                11: {
                    36: width_slice(145,245),
                    42: width_slice(175,245)
                },
                12: {
                    36: width_slice(145,245),
                    42: width_slice(175,245),
                    48: width_slice(175,245),
                },
                14: {
                    42: width_slice(175,245),
                    48: width_slice(175,245),
                    60: width_slice(210,245)
                },
                20: {
                    18: width_slice(145,210),
                    24: width_slice(145,210)
                },
                23: {
                    24: width_slice(140,245),
                    30: width_slice(140,245),
                    36: width_slice(145,245)
                },
                24: {
                    24: width_slice(145,210),
                    30: width_slice(145,210),
                    36: width_slice(145,210),
                    42: width_slice(175,245),
                    48: width_slice(175,245),
                },
                25: {
                    42: width_slice(175,245),
                    48: width_slice(175,245)
                },
                26: {
                    48: width_slice(175,245),
                    60: width_slice(210,245)
                },
                27: {
                    48: width_slice(175,245),
                    60: width_slice(210,245)
                },
                37: {
                    36: width_slice(175,245),
                    42: width_slice(175,245),
                    48: width_slice(175,245),
                    60: width_slice(210,245)
                },
                "3K": {
                    48: width_slice(175,245),
                    60: width_slice(210,245)
                },
                47: {
                    36: width_slice(175,210)
                },
                49: {
                    48: width_slice(210,245),
                    60: width_slice(210,245)
                },
                50: {
                    48: width_slice(210,245),
                    60: width_slice(210,245),
                },
                51: {
                    42: width_slice(210,245),
                    48: width_slice(210,245),
                    60: width_slice(210,245),
                },
                52: {
                    48: [0],
                    60: [0],
                },
                53: {
                    36: [0],
                    42: [0],
                    48: [0],
                },
                54: {
                    48: width_slice(210,245),
                    60: width_slice(210,245),
                },
                55: {
                    48: width_slice(210,245),
                    60: width_slice(210,245),
                },
                72: {
                    60: [0]
                },
                74: {
                    60: [0]
                },
                80: {
                    36: width_slice(145,210)
                },
                81: {
                    36: width_slice(145,210)
                },
                82: {
                    36: width_slice(145,210)
                },
                83: {
                    36: width_slice(145,210)
                },
                86: {
                    48: width_slice(175,245),
                    60: width_slice(210,245)
                },
                88: {
                    48: width_slice(175,245),
                    60: width_slice(210,245)
                },
                91: {
                    18: width_slice(140,210),
                    24: width_slice(140,210),
                    30: width_slice(140,210)
                },
                92: {
                    24: width_slice(140,210),
                    30: width_slice(140,210),
                    36: width_slice(145,210)
                },
                10: {
                    36: width_slice(145,210),
                },
                21: {
                    18: width_slice(140,210),
                    24: width_slice(140,210),
                    30: width_slice(140,210)
                },
                22: {
                    18: width_slice(140,245),
                    24: width_slice(140,245),
                    30: width_slice(140,245),
                    36: width_slice(145,245)
                },
                30: {
                    18: width_slice(140,175),
                    24: width_slice(140,175)
                },
                31: {
                    18: width_slice(140,210),
                    24: width_slice(140,210),
                    30: width_slice(140,210)
                },
                32: {
                    24: width_slice(140,210),
                    30: width_slice(140,210),
                    36: width_slice(145,210)
                },
                "7J": {
                    24: width_slice(145,210),
                    30: width_slice(145,210),
                    36: width_slice(145,210)
                },
                33: {
                    30: width_slice(140, 245),
                    36: width_slice(142, 245)
                },
                "8J": {
                    30: width_slice(140, 245),
                    36: width_slice(145, 245)
                },
                34: {
                    36: width_slice(145, 245),
                    42: width_slice(175, 245)
                },
                "9J": {
                    30: width_slice(140, 245),
                    36: width_slice(145, 245),
                    42: width_slice(175, 245)
                },
                35: {
                    36: width_slice(145, 245),
                    42: width_slice(175, 245),
                    48: width_slice(175, 245)
                },
                "1K": {
                    36: width_slice(145, 245),
                    42: width_slice(175, 245),
                    48: width_slice(175, 245)
                },
                36: {
                    36: width_slice(145, 245),
                    42: width_slice(175, 245),
                    48: width_slice(175, 245),
                    60: width_slice(210, 245)
                },
                "2K": {
                    48: width_slice(175, 245),
                    60: width_slice(210, 245)
                },
                48: {
                    36: width_slice(175, 245),
                    42: width_slice(175, 245),
                    48: width_slice(175, 245),
                    60: width_slice(210, 245)
                },
                84: {
                    42: width_slice(175, 245),
                    48: width_slice(175, 245),
                    60: width_slice(210, 245)
                }
            },
            "04": {
                11: {
                    36: width_slice_uc(140,200),
                    42: width_slice_uc(155,200)
                },
                12: {
                    36: width_slice_uc(140,200),
                    42: width_slice_uc(155,200),
                    48: width_slice_uc(170,200),
                },
                14: {
                    42: width_slice_uc(155,200),
                    48: width_slice_uc(170,200),
                    60: [200]
                },
                20: {
                    18: width_slice_uc(130,155),
                    24: width_slice_uc(130,155)
                },
                23: {
                    24: width_slice_uc(130,200),
                    30: width_slice_uc(130,200),
                    36: width_slice_uc(140,200)
                },
                24: {
                    24: width_slice_uc(140,200),
                    30: width_slice_uc(140,200),
                    36: width_slice_uc(140,200),
                    42: width_slice_uc(155,200),
                    48: width_slice_uc(170,200)
                },
                25: {
                    42: width_slice_uc(155,200),
                    48: width_slice_uc(170,200)
                },
                26: {
                    48: width_slice_uc(170,200),
                    60: [200]
                },
                27: {
                    48: width_slice_uc(170,200),
                    60: [200]
                },
                37: {
                    36: width_slice_uc(140,200),
                    42: width_slice_uc(155,200),
                    48: width_slice_uc(170,200),
                    60: [200]
                },
                "3K": {
                    48: width_slice_uc(170,200),
                    60: [200]
                },
                47: {
                    36: [170,205]
                },
                49: {
                    48: [205],
                    60: [205]
                },
                50: {
                    48: [205],
                    60: [205],
                },
                51: {
                    42: [205],
                    48: [205],
                    60: [205],
                },
                52: {
                    48: [205],
                    60: [205],
                },
                53: {
                    36: [140,170,200],
                    42: width_slice_uc(170,200),
                    48: width_slice_uc(170,200),
                },
                54: {
                    48: [200],
                    60: [200],
                },
                55: {
                    48: [200],
                    60: [200],
                },
                72: {
                    60: [235]
                },
                74: {
                    60: [235]
                },
                80: {
                    36: [140,170]
                },
                81: {
                    36: [140,170]
                },
                82: {
                    36: [140,170]
                },
                83: {
                    36: [140,170]
                },
                86: {
                    48: [170,205],
                    60: [205]
                },
                88: {
                    48: [170,205],
                    60: [205]
                },
                91: {
                    18: width_slice_uc(130,170),
                    24: width_slice_uc(130,170),
                    30: width_slice_uc(130,170)
                },
                92: {
                    24: width_slice_uc(130,170),
                    30: width_slice_uc(130,170),
                    36: width_slice_uc(140,170)
                },
                10: {
                    36: width_slice_uc(140,170),
                },
                21: {
                    18: width_slice_uc(130,170),
                    24: width_slice_uc(130,170),
                    30: width_slice_uc(130,170)
                },
                22: {
                    18: width_slice_uc(130,170),
                    24: width_slice_uc(130,170),
                    30: width_slice_uc(130,170),
                    36: width_slice_uc(140,170)
                },
                30: {
                    18: width_slice_uc(130,155),
                    24: width_slice_uc(130,155)
                },
                31: {
                    18: width_slice_uc(130,170),
                    24: width_slice_uc(130,170),
                    30: width_slice_uc(130,170)
                },
                32: {
                    24: width_slice_uc(130,170),
                    30: width_slice_uc(130,170),
                    36: width_slice_uc(140,170)
                },
                "7J": {
                    24: width_slice_uc(130,170),
                    30: width_slice_uc(130,170),
                    36: width_slice_uc(140,170)
                },
                33: {
                    30: width_slice_uc(130, 200),
                    36: width_slice_uc(140, 200)
                },
                "8J": {
                    30: width_slice_uc(130, 200),
                    36: width_slice_uc(140, 200)
                },
                34: {
                    36: width_slice_uc(140, 200),
                    42: width_slice_uc(155, 200)
                },
                "9J": {
                    30: width_slice_uc(130, 200),
                    36: width_slice_uc(140, 200),
                    42: width_slice_uc(155, 200)
                },
                35: {
                    36: width_slice_uc(140, 200),
                    42: width_slice_uc(155, 200),
                    48: width_slice_uc(170, 200)
                },
                "1K": {
                    36: width_slice_uc(140, 200),
                    42: width_slice_uc(155, 200),
                    48: width_slice_uc(170, 200)
                },
                36: {
                    36: width_slice_uc(140, 200),
                    42: width_slice_uc(155, 200),
                    48: width_slice_uc(170, 200),
                    60: [200]
                },
                "2K": {
                    48: width_slice_uc(170, 200),
                    60: [200]
                },
                48: {
                    36: width_slice_uc(140, 200),
                    42: width_slice_uc(155, 200),
                    48: width_slice_uc(170, 200),
                    60: [200]
                },
                84: {
                    42: [170,205],
                    48: [170,205],
                    60: [205]
                }
            },
            "00": {
                11: {
                    36: width_slice_uc(140,200),
                    42: width_slice_uc(155,200)
                },
                12: {
                    36: width_slice_uc(140,200),
                    42: width_slice_uc(155,200),
                    48: width_slice_uc(170,200),
                },
                14: {
                    42: width_slice_uc(155,200),
                    48: width_slice_uc(170,200),
                    60: [200]
                },
                20: {
                    18: width_slice_uc(130,155),
                    24: width_slice_uc(130,155)
                },
                23: {
                    24: width_slice_uc(130,200),
                    30: width_slice_uc(130,200),
                    36: width_slice_uc(140,200)
                },
                24: {
                    24: width_slice_uc(140,200),
                    30: width_slice_uc(140,200),
                    36: width_slice_uc(140,200),
                    42: width_slice_uc(155,200),
                    48: width_slice_uc(170,200)
                },
                25: {
                    42: width_slice_uc(155,200),
                    48: width_slice_uc(170,200)
                },
                26: {
                    48: width_slice_uc(170,200),
                    60: [200]
                },
                27: {
                    48: width_slice_uc(170,200),
                    60: [200]
                },
                37: {
                    36: width_slice_uc(140,200),
                    42: width_slice_uc(155,200),
                    48: width_slice_uc(170,200),
                    60: [200]
                },
                "3K": {
                    48: width_slice_uc(170,200),
                    60: [200]
                },
                47: {
                    36: [170,205]
                },
                49: {
                    48: [205],
                    60: [205]
                },
                50: {
                    48: [205],
                    60: [205],
                },
                51: {
                    42: [205],
                    48: [205],
                    60: [205],
                },
                52: {
                    48: [205],
                    60: [205],
                },
                53: {
                    36: [140,170,200],
                    42: width_slice_uc(170,200),
                    48: width_slice_uc(170,200),
                },
                54: {
                    48: [200],
                    60: [200],
                },
                55: {
                    48: [200],
                    60: [200],
                },
                72: {
                    60: [235]
                },
                74: {
                    60: [235]
                },
                80: {
                    36: [140,170]
                },
                81: {
                    36: [140,170]
                },
                82: {
                    36: [140,170]
                },
                83: {
                    36: [140,170]
                },
                86: {
                    48: [170,205],
                    60: [205]
                },
                88: {
                    48: [170,205],
                    60: [205]
                },
                91: {
                    18: width_slice_uc(130,170),
                    24: width_slice_uc(130,170),
                    30: width_slice_uc(130,170)
                },
                92: {
                    24: width_slice_uc(130,170),
                    30: width_slice_uc(130,170),
                    36: width_slice_uc(140,170)
                },
                10: {
                    36: width_slice_uc(140,170),
                },
                21: {
                    18: width_slice_uc(130,170),
                    24: width_slice_uc(130,170),
                    30: width_slice_uc(130,170)
                },
                22: {
                    18: width_slice_uc(130,170),
                    24: width_slice_uc(130,170),
                    30: width_slice_uc(130,170),
                    36: width_slice_uc(140,170)
                },
                30: {
                    18: width_slice_uc(130,155),
                    24: width_slice_uc(130,155)
                },
                31: {
                    18: width_slice_uc(130,170),
                    24: width_slice_uc(130,170),
                    30: width_slice_uc(130,170)
                },
                32: {
                    24: width_slice_uc(130,170),
                    30: width_slice_uc(130,170),
                    36: width_slice_uc(140,170)
                },
                "7J": {
                    24: width_slice_uc(130,170),
                    30: width_slice_uc(130,170),
                    36: width_slice_uc(140,170)
                },
                33: {
                    30: width_slice_uc(130, 200),
                    36: width_slice_uc(140, 200)
                },
                "8J": {
                    30: width_slice_uc(130, 200),
                    36: width_slice_uc(140, 200)
                },
                34: {
                    36: width_slice_uc(140, 200),
                    42: width_slice_uc(155, 200)
                },
                "9J": {
                    30: width_slice_uc(130, 200),
                    36: width_slice_uc(140, 200),
                    42: width_slice_uc(155, 200)
                },
                35: {
                    36: width_slice_uc(140, 200),
                    42: width_slice_uc(155, 200),
                    48: width_slice_uc(170, 200)
                },
                "1K": {
                    36: width_slice_uc(140, 200),
                    42: width_slice_uc(155, 200),
                    48: width_slice_uc(170, 200)
                },
                36: {
                    36: width_slice_uc(140, 200),
                    42: width_slice_uc(155, 200),
                    48: width_slice_uc(170, 200),
                    60: [200]
                },
                "2K": {
                    48: width_slice_uc(170, 200),
                    60: [200]
                },
                48: {
                    36: width_slice_uc(140, 200),
                    42: width_slice_uc(155, 200),
                    48: width_slice_uc(170, 200),
                    60: [200]
                },
                84: {
                    42: [170,205],
                    48: [170,205],
                    60: [205]
                }
            }
        }
    }
}