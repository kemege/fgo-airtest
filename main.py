#!/usr/local/bin/python3
# -*- encoding=utf8 -*-
import logging
from airtest.core.api import *
from math import floor
import sys
import traceback
import os
import datetime
from lib.actions import unlimited
import teams.daily
import teams.events

__author__ = "sansui233"

auto_setup(__file__)
connect_device("iOS:///127.0.0.1:8100")


def main():
    setLog()
    if sys.platform == 'win32':
        import win10toast
        G.notifier = win10toast.ToastNotifier()

    try:
        if sys.argv[1] == "-h":
            print("运行方式: python main.py 队伍名 运行次数")
            print('teams/daily.py:\n')
            print('\n'.join(dir(teams.daily)))
            print('\nteams/events.py:\n')
            print('\n'.join(dir(teams.events)))
            return
        try:
            team = getattr(teams.daily, sys.argv[1])
        except:
            team = getattr(teams.events, sys.argv[1])

        print(team.__doc__)
        if sys.argv[2].isdigit():
            wrapTimes(team)(int(sys.argv[2]))
        elif sys.argv[2] == "-a":  # 按苹果数消耗
            apple = 1
            now = 139
            apple = int(sys.argv[3])
            if len(sys.argv) == 4:
                now = int(sys.argv[3])
            wrapTimes(team)(calcRound(apple, now))
        elif sys.argv[2] == "-u":  # 抽无限池
            round = 5
            if len(sys.argv) == 4:
                round = int(sys.argv[3])
            unlimited(round)
        else:
            logging.error("参数错误")
    except Exception as err:
        if sys.platform == 'macos':
            os.system(
                """/usr/bin/osascript -e 'display notification with title \"程序异常退出\"' """
            )
        elif sys.platform == 'win32':
            # notifier = win10toast.ToastNotifier()
            G.notifier.show_toast('FGO-Airtest', "异常退出 %s" % err, threaded=True, duration=5)
        logging.error("异常退出 %s" % err)
        # traceback.print_exc(chain=False)
        exit(1)
    if sys.platform == 'macos':
        os.system("""/usr/bin/osascript -e 'display notification with title \"肝完了\"' """)
    logging.info("肝完了")


def setLog():
    logger = logging.getLogger("airtest")
    logger.setLevel(logging.ERROR)
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s [%(levelname)s] %(message)s')
    logging.getLogger().handlers[0].setFormatter(
        logging.Formatter('%(asctime)s [%(levelname)s] [%(name)s] %(message)s'))


def calcRound(consume=12, now=139, perApple=139):
    """
    在预计消耗苹果的基础上浮动 2 个苹果,使得体力剩余更少

    consume: 消耗苹果数
    now: 目前的体力
    perApple: 一个金苹果的体力
    返回值: 3T编队执行次数
    """
    l = []
    for i in range(-2, 3):
        l.append(((consume + i) * perApple + now) % 40)
    left = min(l)
    i = l.index(left)
    if consume + i - 2 > 0:
        result = floor(((consume + i - 2) * perApple + now) / 40)
        logging.info("消耗 %d 个苹果，剩体力 %d ", consume + i - 2, left)
        return result
    else:
        result = floor((consume * perApple + now) / 40)
        logging.info("消耗 %d 个苹果，剩体力 %d ", consume, l[2])
        return result

# 可以用装饰器的形式加在 def teamfunc 前指定指定次数，但就是，谁会固定 team 的执行次数啊……


def wrapTimes(team_func):
    """
    指定某个函数执行多次

    用法: wrapTimes(afunc: function)(times: int)
    afunc: 目标函数名
    times: 次数
    """
    round = 1

    def wrapped(times: int):
        nonlocal round
        while round <= times:
            logging.info("执行第 %d 轮", round)
            logging.info("剩余执行轮数: %d", times - round)
            try:
                team_func(times - round)
                round += 1
            except Exception as ex:
                snapshot(datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.png')
                logging.error('碰到错误，退出：' + str(ex))
                break

    return wrapped


# 主程序
if __name__ == "__main__":
    main()
