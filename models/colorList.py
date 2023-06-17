# -*- coding:UTF-8 -*-
import numpy as np
import collections


def getColorList():
    dict = collections.defaultdict(list)

    # black
    lower_black = np.array([0, 0, 0])
    upper_black = np.array([180, 255, 46])
    color_list_black = []
    color_list_black.append(lower_black)
    color_list_black.append(upper_black)
    dict['black'] = color_list_black

    # gray
    lower_gray = np.array([0, 0, 46])
    upper_gray = np.array([180, 43, 220])
    color_list_gray= []
    color_list_gray.append(lower_gray)
    color_list_gray.append(upper_gray)
    dict['gray'] = color_list_gray

    # white
    lower_white = np.array([0, 0, 221])
    upper_white = np.array([180, 30, 255])
    color_list_white = []
    color_list_white.append(lower_white)
    color_list_white.append(upper_white)
    dict['white'] = color_list_white

    # red
    lower_red = np.array([156, 43, 46])
    upper_red = np.array([180, 255, 255])
    color_list_red = []
    color_list_red.append(lower_red)
    color_list_red.append(upper_red)
    dict['red'] = color_list_red

    # red2
    lower_red = np.array([0, 43, 46])
    upper_red = np.array([10, 255, 255])
    color_list_red2 = []
    color_list_red2.append(lower_red)
    color_list_red2.append(upper_red)
    dict['red2'] = color_list_red2

    # orange
    lower_orange = np.array([11, 43, 46])
    upper_orange = np.array([25, 255, 255])
    color_list_orange = []
    color_list_orange.append(lower_orange)
    color_list_orange.append(upper_orange)
    dict['orange'] = color_list_orange

    # yellow
    lower_yellow = np.array([26, 43, 46])
    upper_yellow = np.array([34, 255, 255])
    color_list_yellow = []
    color_list_yellow.append(lower_yellow)
    color_list_yellow.append(upper_yellow)
    dict['yellow'] = color_list_yellow

    # green
    lower_green = np.array([35, 43, 46])
    upper_green = np.array([77, 255, 255])
    color_list_green = []
    color_list_green.append(lower_green)
    color_list_green.append(upper_green)
    dict['green'] = color_list_green

    # cyan
    lower_cyan = np.array([78, 43, 46])
    upper_cyan = np.array([99, 255, 255])
    color_list_cyan = []
    color_list_cyan.append(lower_cyan)
    color_list_cyan.append(upper_cyan)
    dict['cyan'] = color_list_cyan

    # blue
    lower_blue = np.array([100, 43, 46])
    upper_blue = np.array([124, 255, 255])
    color_list_blue = []
    color_list_blue.append(lower_blue)
    color_list_blue.append(upper_blue)
    dict['blue'] = color_list_blue

    # purple
    lower_purple = np.array([125, 43, 46])
    upper_purple = np.array([155, 255, 255])
    color_list_purple = []
    color_list_purple.append(lower_purple)
    color_list_purple.append(upper_purple)
    dict['purple'] = color_list_purple

    return dict


if __name__ == '__main__':
    color_dict = getColorList()
    print(color_dict)

    num = len(color_dict)
    print('num=', num)

    for d in color_dict:
        print('key=', d)
        print('upper_value=', color_dict[d][1])