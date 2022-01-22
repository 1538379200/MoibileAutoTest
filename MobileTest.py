import subprocess
import PySimpleGUI as sg
import os
import ast
import time
from bs4 import BeautifulSoup
import numpy as np
from pathlib import Path
import warnings
import eventlet
import re

warnings.simplefilter(action='ignore', category=FutureWarning)  # 忽略全局functionwarning警告
# eventlet.monkey_patch()

list_ = []
screenPic = ''
screenRecordDir = ''

"""adb命令运行代码"""


class adbRun():
    """运行脚本代码实现"""

    def run(self, type_, valueX=None, valueY=None, InputValue=None):
        if type_ == '滑动屏幕':
            X = valueX.split(';')
            Y = valueY.split(';')
            currentX = int(X[0])
            currentY = int(Y[0])
            toX = int(X[1])
            toY = int(Y[1])
            try:
                adbScript = 'adb shell input touchscreen swipe {0} {1} {2} {3}'.format(currentX, currentY, toX, toY)
                os.system(adbScript)
                print('从', currentX, currentY, '移动到', toX, toY, end='\n\n')
            except Exception as e:
                print(f'滑动屏幕{currentX, currentY}到{toX, toY}出错', e, end='\n\n')
        elif type_ == '点击坐标':
            X = int(valueX)
            Y = int(valueY)
            try:
                adbScript = 'adb shell input tap {} {}'.format(X, Y)
                os.system(adbScript)
                print(f'点击坐标：{X, Y}', end='\n\n')
            except Exception as e:
                print(f'点击坐标{X, Y}出错：', e, end='\n\n')
        elif type_ == '输入文字(带ENTER)':
            try:
                if valueX and valueY:
                    X = int(valueX)
                    Y = int(valueY)
                    adbScriptClick = 'adb shell input tap {} {}'.format(X, Y)
                    os.system(adbScriptClick)
                    time.sleep(0.5)
                    adbScript = f'adb shell input text {InputValue}'
                    os.system(adbScript)
                    adbScript2 = 'adb shell input keyevent ENTER'
                    os.system(adbScript2)
                    print(f'输入文字：{InputValue}', end='\n\n')
                else:
                    adbScript = f'adb shell input text {InputValue}'
                    os.system(adbScript)
                    adbScript2 = 'adb shell input keyevent ENTER'
                    os.system(adbScript2)
                    print(f'输入文字：{InputValue}', end='\n\n')
            except Exception as e:
                print(f'输入文字{InputValue}出错：', e, end='\n\n')
        elif type_ == '输入文字(不带ENTER)':
            try:
                if valueX and valueY:
                    X = int(valueX)
                    Y = int(valueY)
                    adbScriptClick = 'adb shell input tap {} {}'.format(X, Y)
                    os.system(adbScriptClick)
                    time.sleep(0.5)
                    adbScript = f'adb shell input text {InputValue}'
                    os.system(adbScript)
                    print(f'输入文字：{InputValue}', end='\n\n')
                else:
                    adbScript = f'adb shell input text {InputValue}'
                    os.system(adbScript)
                    print(f'输入文字：{InputValue}', end='\n\n')
            except Exception as e:
                print(f'输入文字{InputValue}出错：', e, end='\n\n')
        elif type_ == '启动App':
            try:
                if InputValue:
                    adbScript = f'adb shell am start {InputValue}'
                    os.system(adbScript)
                    print('启动App', end='\n\n')
                else:
                    print('没有找到app', end='\n\n')
            except Exception as e:
                print('打开App错误：', e, end='\n\n')
        elif type_ == '等待':
            try:
                if InputValue:
                    for i in range(1, (int(InputValue) + 1)):
                        if i == int(InputValue):
                            print(f'等待{i}秒', end='\n\n')
                        else:
                            print('\r', f'等待{i}秒', end='', flush=True)
                        time.sleep(1)
                else:
                    print('没有输入值', end='\n\n')
            except Exception as e:
                print('等待出错：', e, end='\n\n')
        elif type_ == '返回':
            adbScriptESC = 'adb shell input keyevent BACK'
            os.system(adbScriptESC)
            print('返回', end='\n\n')
        elif type_ == '长按':
            try:
                X = int(valueX)
                Y = int(valueY)
                if InputValue:
                    adbScript = f'adb shell input swipe {X} {Y} {X} {Y} {int(InputValue) * 1000}'
                    tip = int(InputValue)
                else:
                    adbScript = f'adb shell input swipe {X} {Y} {X} {Y} 2000'
                    tip = 2
                os.system(adbScript)
                print(f'长按{tip}秒')
            except Exception as e:
                print('长按操作错误，请检查输入', end='\n\n')
        elif type_ == '截图':
            global screenPic
            try:
                strTime = time.strftime('%Y%m%d%H%M%S')
                if InputValue:
                    picPath = screenPic + '\\' + InputValue + '.png'
                else:
                    picPath = screenPic + '\\' + strTime + '.png'
                if screenPic != '':
                    adbScript = f'adb exec-out screencap -p > {picPath}'
                    os.system(adbScript)
                    print(f'截图({picPath})', end='\n\n')
                else:
                    inputPicPath = sg.popup_get_text('请输入截图保存路径', title='截图提示', size=(60, 4),
                                                     background_color='#ffffff',
                                                     button_color=('#ffffff', '#18A058'), icon='GuiIcon.ico')
                    screenPic = inputPicPath
                    adbScript = f'adb exec-out screencap -p > {picPath}'
                    os.system(adbScript)
                    print(f'截图(位置保存在:{picPath})', end='\n\n')
            except Exception as e:
                print('截图失败，可能是文件位置选择错误', end='\n\n')
        elif type_ == '智能等待':
            try:
                if InputValue:  # 拿到输入框的值，当有值时进行智能等待，否则跳过智能等待
                    waitNum = 1
                    InputValue = str(InputValue.strip())  # 强制转换字符串形式，避免非字符串出错
                    while True:
                        gotXml('waitXml')  # 运行获取手机当前页面元素的方法
                        try:
                            with open('waitXml.xml', 'rb') as f:  # 打开已获取的手机当前页面元素文件
                                xmlFile = f.read()  # 读取xml文件
                                soup = BeautifulSoup(xmlFile, 'xml')  # 解析xml文件
                                boundsText = soup.select(f'node[text*="{InputValue}"]')  # 获取输入的文字，进行元素筛选
                                TextListElNum = len(boundsText)  # 获取元素的列表长度
                                if TextListElNum:  # 当列表中有数据时，则为元素出现，跳出循环
                                    print(f'找到元素："{InputValue}"', end='\n\n')
                                    break
                                elif waitNum == 5:  # 当循环的次数超过5次时，给出2秒强制等待，跳出循环
                                    print('未找到元素，进行强制等待2秒', end='\n\n')
                                    time.sleep(2)
                                    break
                                else:  # 其他情况继续执行元素等待，间隔两秒钟
                                    print(f'第{waitNum}轮等待……', end='')
                                    time.sleep(2)
                                waitNum += 1
                        except Exception as e:
                            print(f'第{waitNum}轮智能等待出错', end='\n\n')
                            if waitNum == 5:
                                break
                            else:
                                waitNum += 1
                                continue
                else:
                    print('等待失败，未输入等待元素', end='\n\n')
            except Exception as e:
                print('智能等待失败', end='\n\n')
            finally:  # 定义一个最后必定执行的finally，在等待操作过后，查找路径中所有的xml文件，将所有文件删除
                delFiles('waitXml')
        elif type_ == '滑动查找':
            try:
                if any((valueX, valueY, InputValue)):
                    checkX = valueX.split(';')
                    checkY = valueY.split(';')
                    currentX = int(checkX[0])
                    currentY = int(checkY[0])
                    toX = int(checkX[1])
                    toY = int(checkY[1])
                    if ';' in InputValue:
                        checkText = InputValue.split(';')[0]
                        checkTimes = int(InputValue.split(';')[1])
                    else:
                        checkText = InputValue
                        checkTimes = False
                    if checkTimes:
                        checkNum = 1
                        for checkel in range(0, checkTimes):
                            checkProgress = sg.OneLineProgressMeter(f'查找元素：{checkText}', checkNum, checkTimes,
                                                                    bar_color='#18A058',
                                                                    button_color='#18A058', )
                            if checkProgress:
                                gotXml('checkFile')
                                try:
                                    with open('checkFile.xml', 'rb') as f:  # 打开已获取的手机当前页面元素文件
                                        checkFile = f.read()  # 读取xml文件
                                        soup = BeautifulSoup(checkFile, 'xml')  # 解析xml文件
                                        boundsText = soup.select(f'node[text*="{checkText}"]')  # 获取输入的文字，进行元素筛选
                                        if len(boundsText) == 0:
                                            adbScript = 'adb shell input touchscreen swipe {0} {1} {2} {3}'.format(
                                                currentX,
                                                currentY,
                                                toX, toY)
                                            subprocess.call(adbScript, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                                            shell=True)
                                            print(f'第{checkNum}轮元素查找……')
                                            checkNum += 1
                                            continue
                                        else:
                                            print(f'已找到元素"{checkText}"', end='\n\n')
                                            break
                                except Exception as e:
                                    checkNum += 1
                                    continue
                            else:
                                print('终止查询……', end='\n\n')
                        if len(boundsText) == 0:
                            print(f'未找到"{checkText}"元素', end='\n\n')
                    else:
                        checkNum = 1
                        while True:
                            checkProgress = sg.OneLineProgressMeter(f'查找元素：{checkText}', checkNum, 100000,
                                                                    bar_color='#18A058',
                                                                    button_color='#18A058', )
                            if checkProgress:
                                gotXml('checkFile')
                                try:
                                    with open('checkFile.xml', 'rb') as f:  # 打开已获取的手机当前页面元素文件
                                        checkFile = f.read()  # 读取xml文件
                                        soup = BeautifulSoup(checkFile, 'xml')  # 解析xml文件
                                        boundsText = soup.select(f'node[text*="{checkText}"]')  # 获取输入的文字，进行元素筛选
                                        if len(boundsText) == 0:
                                            adbScript = 'adb shell input touchscreen swipe {0} {1} {2} {3}'.format(
                                                currentX,
                                                currentY,
                                                toX, toY)
                                            subprocess.call(adbScript, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                                            shell=True)
                                            print(f'第{checkNum}轮元素查找……')
                                            checkNum += 1
                                            continue
                                        else:
                                            print(f'已找到元素"{checkText}"', end='\n\n')
                                            break
                                except Exception as e:
                                    checkNum += 1
                                    continue
                            else:
                                print('终止查询……', end='\n\n')
                                break
                        if len(boundsText) == 0:
                            print(f'未找到"{checkText}"元素', end='\n\n')
                else:
                    print('查找失败，输入数据不完整', end='\n\n')
            except:
                print('查找失败，请确认输入', end='\n\n')
            finally:
                delFiles('checkFile')
        elif type_ == '元素点击':
            if InputValue:
                if ';' in InputValue:
                    clickType = InputValue.split(';')[0]
                    clickText = InputValue.split(';')[1]
                else:
                    clickType = 'text'
                    clickText = InputValue
                try:
                    gotXml('clickFile')
                    with open('clickFile.xml', 'rb') as f:  # 打开已获取的手机当前页面元素文件
                        checkFile = f.read()  # 读取xml文件
                        soup = BeautifulSoup(checkFile, 'xml')  # 解析xml文件
                        boundsText = soup.select(f'node[{clickType}*="{clickText}"]')  # 获取输入的文字，进行元素筛选
                        if len(boundsText) == 0:
                            print(f'当前页面未找到“{InputValue}"元素', end='\n\n')
                        else:
                            clickAble = False
                            for elNum in range(len(boundsText)):
                                if '[0,0]' in boundsText[elNum]['bounds']:
                                    pass
                                else:
                                    replaceBounds = boundsText[elNum]['bounds'].replace('[', '').replace(']', ',')
                                    boudsList = replaceBounds.split(',')  # 字符串格式替换特殊字符，形成需要的列表
                                    x = int(boudsList[2]) - ((int(boudsList[2]) - int(boudsList[0])) / 2)
                                    y = int(boudsList[3]) - ((int(boudsList[3]) - int(boudsList[1])) / 2)
                                    subprocess.call(f'adb shell input tap {x} {y}', stdout=subprocess.PIPE,
                                                    stderr=subprocess.STDOUT, shell=True)
                                    clickAble = True
                                    print(f'找到"{clickText}"元素，并进行点击……', end='\n\n')
                                    break
                            if clickAble is False:
                                print('未能准确找到元素进行点击操作，请尝试其他定位或点击方式', end='\n\n')
                except Exception as e:
                    print('运行错误，可能没有获得源文件或者运行错误', end='\n\n')
                finally:
                    delFiles('clickFile')
            else:
                print('操作失败，未输入需要点击的元素', end='\n\n')
        else:
            print('操作状态可能包含空格等不正确信息，不能操作', end='\n\n')


"""定义一个删除手机文件和本地存储文件的代码"""


def delFiles(filename):
    subprocess.call(f'adb shell rm /sdcard/{filename}.xml', stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT, shell=True)
    allXmlNames = Path(__file__).resolve().parent.glob('*.xml')  # 获取路径下所有带.xml的文件
    if allXmlNames:
        for xmlFile in allXmlNames:  # 查询xml文件并删除
            Path.unlink(xmlFile)


"""" 进行脚本操作代码 """


class ScriptControl():
    """ 保存脚本代码实现 """

    def saveScrips(self, filename):
        try:
            if filename:
                with open(filename, 'w', encoding='utf8') as w:
                    w.write(str(list_))
                    w.close()
                sg.popup('已保存脚本', title='提示', background_color='#ffffff', button_color=('#ffffff', '#18A058'),
                         icon='GuiIcon.ico')
            else:
                print('取消操作', end='\n\n')
        except Exception as e:
            print('保存出错：', e, end='\n\n')

    """读取脚本文件代码实现，读取直接运行脚本"""

    def readScripts(self, testScript):
        try:
            if testScript:
                print('*-' * 27, '开始测试', '-*' * 27, end='\n\n')
                with open(testScript, 'r', encoding='utf8') as f:
                    testCases = f.read()
                    testCasesList = ast.literal_eval(testCases)  # 将列表形式的字符串转换为list格式
                    num = 1
                    for i in testCasesList:
                        adbRun().run(type_=i[0], valueX=i[1], valueY=i[2], InputValue=i[3])
                        sg.OneLineProgressMeter('测试进度：', num, len(testCasesList), bar_color='#18A058',
                                                button_color='#18A058', )
                        num += 1
                    sg.popup('测试完成!', title='提示', line_width=1000, background_color='#ffffff',
                             button_color=('#ffffff', '#18A058'), icon='GuiIcon.ico')
                print('*-' * 27, '测试完成', '-*' * 27, end='\n\n')
            else:
                print('未选择文件', end='\n\n')
        except Exception as e:
            print('读取错误：', e, '\n\n')


"""实现页面自动获取元素，并计算元素坐标中间值"""


def gotXml(file):
    # os.system(f'adb shell uiautomator dump --compressed /sdcard/{file}.xml')  # 定义adb获取页面元素的外部命令
    # os.system(f'adb pull /sdcard/{file}.xml {file}.xml')  # 经xml文件推送至当前目录
    # os.system(f'adb shell rm /sdcard/{file}.xml')  # 删除手机上保存的xml文件
    subprocess.call(f'adb shell uiautomator dump --compressed /sdcard/{file}.xml', stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT, shell=True)  # 定义adb获取页面元素的外部命令
    subprocess.call(f'adb pull /sdcard/{file}.xml {file}.xml', stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT, shell=True)


def checkXml(type_, file):
    CanChoiceTextList = []  # 定义保存可点击元素文本的列表
    CanChoiceAxisList = []  # 定义保存坐标值的列表
    warningMsgTuple = ''
    try:
        with open(file + '.xml', 'rb') as f:
            xmlFile = f.read()  # 读取xml文件
            soup = BeautifulSoup(xmlFile, 'xml')  # 解析xml文件
            boundsText = soup.select(f'node[{type_}]')  # 获取定位方式的标签
            for i in range(0, len(boundsText)):  # 循环所有的标签，找出定位属性的值，加入文本列表中
                XmlText = soup.select(f'node[{type_}]')[i][f'{type_}']
                # XmlTextFilter = re.findall(r'[\u4e00-\u9fa5]+[0-9A-Za-z]',XmlText) # 使用正则匹配，获取只有中文、英文、数字的数据
                # print(XmlTextFilter)
                if XmlText:
                    if isinstance(XmlText, str):
                        # XmlText = XmlText.replace('\n','').replace('.','').replace('/','').replace('\\','')
                        pass
                    else:
                        XmlText = str(XmlText)
                    XmlTextFilter = XmlText.split('\n')[0].split(',')[0].split('\\')[0].split('/')[0].split('.')[0]
                    CanChoiceTextList.append(XmlTextFilter)
                # print(XmlTextFilter)
            GotTextNameList = []  # 可能作为键存在，会有相同元素，所以临时列表作为替用键存在
            beforeTextList = []  # 定义一个已循环出的数据列表，用来判断是否需要更改文本名字
            barNum = 1  # 制作一个进度条的初始值
            maxBar = len(CanChoiceTextList)  # 制作一个总的进度条数
            for textel in CanChoiceTextList:
                tableprogress = sg.OneLineProgressMeter('查找进度：', barNum, maxBar - 1, bar_color='#18A058',
                                                        button_color='#18A058', orientation='h')
                if tableprogress is False:
                    print('取消查找', end='\n\n')
                    break
                try:
                    try:
                        tupleList = np.array(beforeTextList)  # 使用numpy进行列表化，接管列表
                        nums = len(np.where(tupleList == str(textel))[0])  # 获取已存在值的下标列表，获取长度，得到已存在元素个数
                        if nums:
                            GotTextNameList.append(textel + str(nums))
                        else:
                            GotTextNameList.append(textel)
                    except:
                        nums = 0
                        GotTextNameList.append(textel)
                    # print(f'{textel}总数：', nums)
                    # if soup.select(f'node[{type_}*="{textel}"]')[nums]['clickable'] == 'true':  # 当元素可点击时
                    if '[0,0]' not in soup.select(f'node[{type_}*="{textel}"]')[nums]['bounds']:
                        XmlAxis = soup.select(f'node[{type_}*="{textel}"]')[nums]['bounds']  # bounds等于是两个对角的坐标
                    else:
                        try:
                            # print(f'"{textel}"文本元素不能点击，尝试寻找父级……', end='\n\n')  # 当元素不能点击时去循环他的父级元素
                            msg = f'"{textel}"文本元素不能点击，尝试寻找父级……\n\n'
                            warningMsgTuple = warningMsgTuple + msg
                            allFathers = soup.select(f'node[{type_}*="{textel}"]')[nums].parents
                            for childIdex_, childEl in enumerate(allFathers):
                                msg = f'寻找 {textel} 的 {childIdex_ + 1} 级父级元素……\n'
                                warningMsgTuple = warningMsgTuple + msg
                                try:
                                    # childClickable = childEl['clickable']
                                    childAx = childEl['bounds']
                                    # if childClickable == 'true':  # 当父级元素可点击时
                                    if '[0,0]' not in childAx:
                                        XmlAxis = childEl['bounds']
                                        warningMsgTuple = warningMsgTuple + '\n\n'
                                        break
                                    else:
                                        continue
                                except:
                                    continue
                            if XmlAxis is False:
                                msg = f'未找到"{textel}"可点击的父级元素\n\n'
                                warningMsgTuple = warningMsgTuple + msg
                                CanChoiceAxisList.append(['未定位', '未定位'])
                                beforeTextList.append(textel)
                                barNum += 1
                                continue
                        except Exception as e:
                            msg = f'{textel}未找到父级元素\n\n'
                            warningMsgTuple = warningMsgTuple + msg
                            CanChoiceAxisList.append(['未定位', '未定位'])
                            beforeTextList.append(textel)
                            barNum += 1
                            continue
                    replaceBounds = XmlAxis.replace('[', '').replace(']', ',')
                    boudsList = replaceBounds.split(',')  # 字符串格式替换特殊字符，形成需要的列表
                    # 根据bounds获取xy的坐标，bounds相当于一个正方形的左上角和右下角坐标
                    # 因此，只需要求出，bounds两个x的中位数，和两个y坐标的中位数，即可得到元素的中间坐标
                    # 使用 '后一个x-((后一个x-前一个x)/2)' 即可得到中位数
                    # 也可以使用numpy去进行简单的中位数计算，不需要像我自己写公式
                    x = int(boudsList[2]) - ((int(boudsList[2]) - int(boudsList[0])) / 2)
                    y = int(boudsList[3]) - ((int(boudsList[3]) - int(boudsList[1])) / 2)
                    CanChoiceAxisList.append([x, y])  # 将得到的中位数坐标加入列表
                    beforeTextList.append(textel)  # 将已经获取过的元素加入到列表，作为下一个元素的判断条件
                except Exception as e:
                    # print(textel,'获取出错，请尝试其他定位方式')
                    # print('定位坐标：', f"{textel}", '可能获取元素出错，请查看是否有定位显示或者尝试其他定位', end='\n\n')
                    CanChoiceAxisList.append(['未定位', '未定位'])
                    msg = f'定位坐标："{textel}"可能获取元素出错，请查看是否有定位显示或者尝试其他定位\n\n'
                    beforeTextList.append(textel)
                    warningMsgTuple = warningMsgTuple + msg
                    pass
                barNum += 1
        dictAxis = dict(zip(GotTextNameList, CanChoiceAxisList))  # 拼接两个列表，将其转换为字典形式输出
        return dictAxis
    except Exception as e:
        # print('获取定位出错，可能选择的定位类型有误', end='\n\n')
        msg = '获取定位出错，可能选择的定位类型有误\n\n'
        warningMsgTuple = warningMsgTuple + msg
        return 'null'
    finally:
        delFiles(file)
        if warningMsgTuple:
            sg.popup_scrolled(warningMsgTuple, title='查询错误记录', background_color='#ffffff',
                              button_color=('#ffffff', '#18A058'),
                              icon='GuiIcon.ico', non_blocking=True, font=('微软雅黑', 10), text_color='red')


"""获取手机屏幕尺寸的方法"""


def getMobileSize():
    byteSize = subprocess.Popen('adb shell wm size', stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                shell=True).stdout.read()
    mobileSize = str(byteSize).split(' ')[2].split('\\')[0]
    return mobileSize

"""定义获取Ouput框数据的方法"""
def getOutPutData():
    putValue = window['OutPut'].get()  # 获取ouput框中的所有内容
    fil1 = putValue.split('\n')  # 换行符切割，得到一个列表
    putList = []  # 定义一个包含替换的列表
    for i in range(0, len(fil1) - 1):  # 循环切割的列表
        putID = fil1[i].split('：')[0]  # 获取切割列表的序号ID
        try:
            int(putID.strip())  # 去除空格并转换成整数形式
            if '返回' in fil1[i]:  # 如果循环出来的是一个返回操作，则直接返回列表中
                putList.append(['返回', '', '', ''])
            elif '启动App' in fil1[i]:  # 如果返回的是启动App，进行如下处理
                filterStrartApp = fil1[i].split('添加操作：-----> 自动启动App：')[1].strip()
                putList.append(['启动App', '', '', filterStrartApp])
            else:  # 其他情况都使用下面的处理方案
                filterList = fil1[i].split('添加操作：----->')[1].split('；')  # 进行两次切割
                # print(filterList)
                type_ = filterList[0].strip()  # 取出的操作类型去除空格
                valueX = filterList[1].split('：')[1].strip()  # 取出的x坐标切割并去除空格
                valueY = filterList[2].split('：')[1].strip()  # 取出的y坐标切割并去除空格
                valueInput = filterList[3].split('：')[1].strip()  # 取出的输入切割并去除空格
                putList.append([type_, valueX, valueY, valueInput])  # 将准备好的格式已列表形式添加到pulist的列表中
        except:
            pass
    return putList

"""定义运行测试用例的方法"""
def runTestCase():
    try:
        devicesName = os.popen('adb devices')  # 获取是否连接设备
        devicesNameRead = devicesName.read()
        devicesNameFilter = devicesNameRead.split('\n')[1]
        devicesName.close()
        if devicesNameFilter:
            print('已成功连接设备：', devicesNameFilter, end='\n\n')
            print('*-' * 27, '开始测试', '-*' * 27, end='\n\n')
            num = 1  # 进度条初始值
            for i in list_:
                adbRun().run(i[0], i[1], i[2], i[3])
                testProgress = sg.OneLineProgressMeter('测试进度：', num, len(list_), bar_color='#18A058',
                                                       button_color='#18A058', orientation='h')
                if testProgress is False:
                    print('取消测试', end='\n\n')
                    break
                num += 1
            print('*-' * 27, '测试完成', '-*' * 27, end='\n\n')
            sg.popup('测试完成!', title='提示', line_width=1000, background_color='#ffffff',
                     button_color=('#ffffff', '#18A058'), icon='GuiIcon.ico')
        else:
            sg.popup('您还没有正确连接设备，请检查设备情况', title='提示', background_color='#ffffff',
                     button_color=('#ffffff', '#18A058'), icon='GuiIcon.ico')
            print('没有设备连接', end='\n\n')
    except Exception as e:
        print('脚本操作可能包含空格等不正确字符，请重新设置')

"""进行页面布局的代码"""
# sg.theme('DarkAmber')  # 设置当前主题
sg.theme('LightBrown3')
# 界面布局，将会按照列表顺序从上往下依次排列，二级列表中，从左往右依此排列
tipInfo = '滑动和点击会关注X和Y坐标，输入、等待和启动App关注文字输入框\n无键盘不进行ENTER确认输入'
layout = [
    [sg.Text('移动端自动化', font=('微软雅黑', 20), background_color='#ffffff', text_color='#18A058')],
    [sg.T('', font=('微软雅黑', 10), background_color='#ffffff', text_color='#18A058', key='mobileSize')],
    [sg.Text('请选择操作：', background_color='#ffffff'),
     sg.DropDown(values=['启动App', '点击坐标', '滑动屏幕', '输入文字(带ENTER)', '输入文字(不带ENTER)', '等待', '长按', '智能等待', '滑动查找', '元素点击'],
                 default_value='点击坐标', size=20,
                 tooltip=tipInfo, background_color='#ffffff',
                 button_background_color='#18A058', readonly=True),  # values0
     sg.Button('自动获取并填入当前打开的App包名和activity', button_color='#18A058', font=('微软雅黑', 9),
               tooltip='这会自动获取打开的App包名和activity并添加到运行脚本中'),
     sg.T('输入文字如果输入了坐标则操作为点击后输入', background_color='#ffffff'),
     sg.Button('添加截图', tooltip='在界面进行截图', button_color='#18A058', font=('微软雅黑', 9), pad=((140, 0), (0, 0))),
     sg.Button('添加返回操作', tooltip='这在关闭键盘等操作中会很有用', button_color='#18A058', font=('微软雅黑', 9))],
    [sg.T('请输入X坐标：', background_color='#ffffff'), sg.Input(expand_x=True, key='seralX'),
     sg.T('<--滑动传入当前和需要到达的的两个X坐标，英文分号(;)隔开', background_color='#ffffff')],
    [sg.T('请输入Y坐标：', background_color='#ffffff'), sg.Input(expand_x=True, key='seralY'),
     sg.Text('<--滑动传入当前和需要到达的两个Y坐标，英文分号(;)隔开', background_color='#ffffff')],
    [sg.Text('1、在此输入文字。2、启动App将包名和activity放此处，/分隔，形如：com.package.name'
             '/com.package.name.MainActivity。\n3、等待直接写入数字(秒)。4、长按不写时间默认2秒： 5、智能等待需要写好等待的元素，目前仅支持页面文字，\
             \n6、滑动查找在输入滑动坐标后，下面输入框可以单独输入需要查找的文字元素,默认查找10000轮，如果需要自定义查找轮次，\n需要在文字后面加上英文的分号(;)并在其后输入等待的轮次，\
             比如等待“猫”元素，等待10轮：猫;10\n7、元素点击需要传入需要点击的元素文本，默认text方式，自定义方式需用英文(;)隔开，比如需要使用content-desc点击元素”微信“： content-desc;微信 ↓↓↓↓↓↓↓↓↓↓',
             background_color='#ffffff')],
    [sg.Input(expand_x=True, do_not_clear=False, tooltip='目前仅支持英文输入，\n使用中文请搜索adb中文输入法')],  # values1
    [sg.T('此为自动获取当前页面元素，并转换为坐标值，常用 text 和 content-desc ,建议 text,点击将弹出类型输入，输入如：text-->', background_color='#ffffff'),
     sg.Button('获取页面元素坐标', expand_x=True, button_color='#18A058', font=('微软雅黑', 9)),
     sg.B('查看测试队列',button_color='#18A058', font=('微软雅黑', 9))],
    [sg.Output(size=(120, 20), font=('微软雅黑', 12), key='OutPut')],
    [sg.Button('插入操作', size=(24, 1), button_color='#18A058', font=('微软雅黑', 10), pad=((35, 0), (0, 0))),
     sg.Button('保存脚本', size=(24, 1), button_color='#18A058', font=('微软雅黑', 10)),
     sg.Button('读取脚本文件', size=(24, 1), button_color='#18A058', font=('微软雅黑', 10)),
     sg.Button('替换原数据', size=(24, 1), button_color='#18A058', font=('微软雅黑', 10)),
     sg.Button('清空数据', size=(24, 1), button_color='#18A058', font=('微软雅黑', 10)), ],
    [sg.Button('提交测试', size=10, expand_x=True, button_color='#18A058', font=('微软雅黑', 10))]
]

"""客户端事件获取和值获取的代码"""
# 创造窗口
window = sg.Window('移动自动化程序', layout, background_color='#ffffff', icon='GuiIcon.ico', finalize=True)

# 事件循环并获取输入值
num = 1
stringOut = ''
subprocess.call(r'taskkill /f /t /im adb.exe', stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
subprocess.call('adb devices', stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
mobileSize = getMobileSize()
window['mobileSize'].update(value=f'当前手机分辨率：{mobileSize}')
while True:
    event, values = window.read()
    if event is None:  # 如果用户关闭窗口或点击`Cancel`
        # os.system('adb kill-server')
        subprocess.call(r'taskkill /f /t /im adb.exe', stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        break
    # 插入操作显示界面上，并将数据加入list_列表
    elif event == '插入操作':
        seralX = window['seralX'].get()
        seralY = window['seralY'].get()
        # if any([values[1], values[2], values[3]]):
        if any([values[0], seralX, seralY]):
            # print(num, '：', '添加操作：----->', values[0], '；', '输入X坐标：', values[1], '；', '输入的Y坐标：', values[2], '；', '输入：',
            #       values[3], end='\n\n')
            print(num, '：', '添加操作：----->', values[0], '；', '输入X坐标：', seralX, '；', '输入的Y坐标：', seralY, '；', '输入：',
                  values[1], '\n')
            # window['OutPut'].update(value=stringOut)
            # list_.append([values[0], values[1], values[2], values[3]])
            list_.append([values[0], str(seralX), str(seralY), values[1]])
            num += 1
        else:
            sg.popup('添加操作类型失败，请输入完整脚本数据', title='插入错误', background_color='#ffffff',
                     button_color=('#ffffff', '#18A058'), icon='GuiIcon.ico')
            print('请输入完整的脚本数据', end='\n\n')
        window['seralX'].update(value='')
        window['seralY'].update(value='')
    # 点击提交测试，循环list_列表值运行
    elif event == '提交测试':
            if list_ == getOutPutData():
                runTestCase()
            else:
                comMsg = sg.popup('Ouput中的元素已被修改，是否不替换仍使用原数据？',title='提示', background_color='#ffffff',
                             button_color=('#ffffff', '#18A058'), icon='GuiIcon.ico', custom_text=('Yes','No'))
                if comMsg == 'Yes':
                    runTestCase()
                else:
                    print('已取消操作，如需替换，请点击”替换原数据“后进行测试\n')
    # 点击保存脚本按钮，出现弹窗，输入文件名进行保存
    elif event == '保存脚本':
        filename = sg.popup_get_text('请输入脚本文件名(带后缀,可传入路径，建议txt格式，不要使用表格等)', title='提示', size=(60, 4),
                                     background_color='#ffffff',
                                     button_color='#18A058', icon='GuiIcon.ico')
        ScriptControl().saveScrips(filename)
    # 点击读取脚本，选择文件，获取文件路径
    elif event == '读取脚本文件':
        myScript = sg.popup_get_file('请选择上传的脚本,点击OK则立即开始测试', size=(30, 3), title='提示', background_color='#ffffff',
                                     button_color='#18A058', icon='GuiIcon.ico')
        devicesName = os.popen('adb devices')
        devicesNameRead = devicesName.read()
        devicesNameFilter = devicesNameRead.split('\n')[1]
        devicesName.close()
        if devicesNameFilter:
            try:
                print('已成功连接设备：', devicesNameFilter, end='\n\n')
                ScriptControl().readScripts(myScript)
            except:
                print('文件运行出错，请检查文件内容正确性')
        else:
            sg.popup('您还没有正确连接设备，请检查设备状态', title='提示', background_color='#ffffff', button_color=('#ffffff', '#18A058'),
                     icon='GuiIcon.ico')
            print('没有设备连接', end='\n\n')
    elif event == '自动获取并填入当前打开的App包名和activity':
        """给获取包名的方法添加一个验证设备连接状态的方法"""
        devicesName = os.popen('adb devices')
        devicesNameRead = devicesName.read()
        devicesNameFilter = devicesNameRead.split('\n')[1]
        devicesName.close()
        if devicesNameFilter:
            AppName = os.popen('adb shell dumpsys window|findstr mCurrentFocus')
            AppNameText = AppName.read()
            AppNameTextFilter = AppNameText.split(' ')[-1].split('}')[0]
            list_.append(['启动App', '', '', AppNameTextFilter])
            print(num, '：', '添加操作：----->', '自动启动App：', AppNameTextFilter, end='\n\n')
            AppName.close()
            num += 1
        else:
            sg.popup('设备未正常连接，请先连接设备！', title='错误', background_color='#ffffff', button_color=('#ffffff', '#18A058'),
                     icon='GuiIcon.ico')
    elif event == '添加返回操作':
        list_.append(['返回', '', '', ''])
        print(num, '：', '添加操作：----->按下返回键，可能用来关闭键盘等操作', end='\n\n')
        num += 1
    elif event == '清空数据':
        num = 1
        list_ = []
        window['OutPut'].update(value='')
        sg.popup('已清空执行列表和显示窗口，请重新设置数据', title='清空提示', background_color='#ffffff', button_color=('#ffffff', '#18A058'),
                 icon='GuiIcon.ico')
    elif event == '替换原数据':
        try:
            list_ = getOutPutData()  # 将putlist的数据赋值给真正保存测试队列的list_
            window['OutPut'].update(value='')  # 清空整个ouput输出显示框
            print('已替换数据，请确认：', end='\n\n')
            for index_, value_ in enumerate(list_):  # 取出列表的序列号和值
                print(index_ + 1, '：', '添加操作：----->', value_[0], '；', '输入X坐标：', value_[1], '；', '输入的Y坐标：', value_[2],
                      '；', '输入：',
                      value_[3], end='\n\n')  # 将数据打印在output中
            num = len(list_) + 1  # 显示的序号总量用列表数量加1，替换过后，加入的序号可重新从此数字开始
        except:
            print('没有数据需要修改', end='\n\n')
    elif event == '添加截图':
        if screenPic:
            list_.append(['截图', '', '', ''])
            print(num, '：', '添加操作：----->', '截图', '；', '输入X坐标：', '', '；', '输入的Y坐标：', '', '；', '输入：',
                  '', '\n')
            num += 1
        else:
            PicPath = sg.popup_get_text('请输入截图的保存路径')
            screenPic = PicPath
            list_.append(['截图', '', '', ''])
            print(num, '：', '添加操作：----->', '截图', '；', '输入X坐标：', '', '；', '输入的Y坐标：', '', '；', '输入：',
                  '', '\n')
            num += 1
    elif event == '获取页面元素坐标':
        devicesName = os.popen('adb devices')  # 获取是否连接设备
        devicesNameRead = devicesName.read()
        devicesNameFilter = devicesNameRead.split('\n')[1]
        devicesName.close()
        if devicesNameFilter:
            AxisType = sg.popup_get_text('请填入定位的类型(例：text 或 content-desc)', title='输入类型', background_color='#ffffff',
                                         button_color=('#ffffff', '#18A058'),
                                         icon='GuiIcon.ico', default_text='text')  # 弹出窗口，给用户输入定位的方式
            if AxisType:  # 当用户输入了定位方式，则运行下面的代码，否则视为取消操作
                layout2 = [  # 创建第二个window窗口
                    [sg.Text('请输入可点击元素序号：', background_color='#ffffff'),
                     sg.Input(size=(20, 1), key='rowNum'),
                     sg.Button('确认填入', button_color='#18A058')],
                    [sg.Table(values=[["        ", "       "]], key='clickableOut',  # 数据展示的主要组件，一个表格组件
                              auto_size_columns=True, display_row_numbers=True, justification='center',
                              font=('微软雅黑', 12), headings=['元素名', '坐标'],
                              num_rows=15, row_height=40, max_col_width=200, expand_x=True,
                              background_color='#ffffff', header_background_color='#18A058',
                              header_text_color='#ffffff', enable_click_events=True, enable_events=True)],
                ]
                window2 = sg.Window('页面可点击元素', layout2, background_color='#ffffff', icon='GuiIcon.ico', resizable=True,
                                    finalize=True)
                sg.popup_auto_close('正在搜集数据源……', title='提示', background_color='#ffffff', auto_close_duration=2,
                                    button_color='#18A058', icon='GuiIcon.ico', non_blocking=True)
                gotXml('elementMobile')  # 运行获取手机页面xml元素的脚本
                filePath = Path(__file__).resolve().parent / 'elementMobile.xml'
                if filePath.exists():
                    axisEl = checkXml(AxisType, 'elementMobile')  # 运行筛选页面元素定位的方法，获取一个字典，包含元素和坐标
                    # axisString = ''
                    if axisEl == 'null':  # 当获取到的是一个返回的null字符串，则给出提示并退出窗口
                        sg.popup('元素查找出错，或者没有元素', title='提示', background_color='#ffffff',
                                 button_color=('#ffffff', '#18A058'),
                                 icon='GuiIcon.ico')
                        window2.close()
                    elif len(axisEl.values()) == 0:  # 判断获取的列表为空时，给出提示并关闭窗口
                        sg.popup('未找到可用元素，请尝试其他元素', title='提示', background_color='#ffffff',
                                 button_color=('#ffffff', '#18A058'),
                                 icon='GuiIcon.ico')
                        window2.close()
                    else:
                        axisString = []
                        for elindex, elvalue in enumerate(axisEl.items()):  # 循环坐标字典中的值
                            axisString.append([str(elvalue[0]), str(elvalue[1])])  # 将x和y坐标取出，以列表的形式放入列表
                        window2['clickableOut'].update(values=axisString)  # 把上一步添加数据的列表放入表格当中
                        while True:
                            event2, values2 = window2.read()
                            if event2 is None:  # 当用户点击关闭时跳出循环
                                window2.close()
                                break
                            elif event2 == '确认填入':  # 当用户点击确认输入的事件
                                # if values2[0]:  # 如果用户输入了序号，则进行下面的步骤，否则给出错误提示
                                valueTableID = window2['rowNum'].get()
                                if valueTableID:
                                    try:
                                        seral = int(valueTableID)
                                        choiceSeral = list(axisEl.values())[seral]  # 根据序号值，在列表中进行数据选取
                                        window['seralX'].update(value=int(choiceSeral[0]))
                                        window['seralY'].update(value=int(choiceSeral[1]))  # 在主窗口中的x和y输入框更新值
                                        print(f'已填入序号{seral}坐标', end='\n\n')
                                        window2.close()  # 在用户进行坐标填入后直接关闭当前窗口，也就是只能执行一次添加操作
                                        break
                                    except:
                                        print('输入的序号有误，请重新输入', end='\n\n')
                                else:
                                    print('请先选择需要输入的序号', end='\n\n')
                            elif event2 == 'clickableOut':
                                tableRow = values2['clickableOut'][0]
                                window2['rowNum'].update(value=tableRow)
                else:
                    sg.popup('adb获取定位源数据失败', title='提示', background_color='#ffffff',
                             button_color=('#ffffff', '#18A058'),
                             icon='GuiIcon.ico')
                    window2.close()
            else:
                print('取消查找', end='\n\n')
            subprocess.call(f'adb shell rm /sdcard/elementMobile.xml', stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, shell=True)
        else:
            sg.popup('设备未正常连接，请先连接设备再进行坐标获取', title='查找坐标', background_color='#ffffff',
                     button_color=('#ffffff', '#18A058'),
                     icon='GuiIcon.ico')
    elif event == '查看测试队列':
        window['OutPut'].update(value='当前测试队列：\n\n')
        for caseIndex,testCase in enumerate(list_):
            caseType = testCase[0]
            caseX = testCase[1]
            caseY = testCase[2]
            caseInput = testCase[3]
            print(str(caseIndex+1), '：', '添加操作：----->', caseType, '；', '输入X坐标：', caseX, '；', '输入的Y坐标：', caseY, '；', '输入：',
                  caseInput, '\n')
    else:
        sg.popup('无效操作', title='提示', background_color='#ffffff', button_color=('#ffffff', '#18A058'),
                 icon='GuiIcon.ico')
window.close()
