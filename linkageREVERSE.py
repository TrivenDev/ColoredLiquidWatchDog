#!/usr/bin/python3
import numpy as np
from matplotlib import pyplot as plt
import matplotlib.animation as animation

linkageLenA = 22
linkageLenB = 36.9127
linkageLenC = 19.6543
linkageLenD = 32.5225

linkageLenE = 12.5

sizeFont = 7

servoNumCtrl = [0, 1]
servoDirection = [1, -1]


def limitCheck(posInput, circlePos, circleLen, outline):  # E
    circleRx = posInput[0] - circlePos[0]
    circleRy = posInput[1] - circlePos[1]
    realPosSquare = circleRx * circleRx + circleRy * circleRy
    shortRadiusSquare = np.square(circleLen[1] - circleLen[0])
    longRadiusSquare = np.square(circleLen[1] + circleLen[0])

    if realPosSquare >= shortRadiusSquare and realPosSquare <= longRadiusSquare:
        return posInput[0], posInput[1]

    else:
        lineK = (posInput[1] - circlePos[1]) / (posInput[0] - circlePos[0])
        lineB = circlePos[1] - (lineK * circlePos[0])

        if realPosSquare < shortRadiusSquare:
            aX = 1 + lineK * lineK
            bX = 2 * lineK * (lineB - circlePos[1]) - 2 * circlePos[0]
            cX = circlePos[0] * circlePos[0] + (lineB - circlePos[1]) * (lineB - circlePos[1]) - shortRadiusSquare

            resultX = bX * bX - 4 * aX * cX
            x1 = (-bX + np.sqrt(resultX)) / (2 * aX)
            x2 = (-bX - np.sqrt(resultX)) / (2 * aX)

            y1 = lineK * x1 + lineB
            y2 = lineK * x2 + lineB

            if posInput[0] > circlePos[0]:
                if x1 > circlePos[0]:
                    xGenOut = x1 + outline
                    yGenOut = y1
                else:
                    xGenOut = x2 - outline
                    yGenOut = y2
            elif posInput[0] < circlePos[0]:
                if x1 < circlePos[0]:
                    xGenOut = x1 - outline
                    yGenOut = y1
                else:
                    xGenOut = x2 + outline
                    yGenOut = y2
            elif posInput[0] == circlePos[0]:
                if posInput[1] > circlePos[1]:
                    if y1 > circlePos[1]:
                        xGenOut = x1
                        yGenOut = y1 + outline
                    else:
                        xGenOut = x2
                        yGenOut = y2 - outline

            return xGenOut, yGenOut

        elif realPosSquare > longRadiusSquare:
            aX = 1 + lineK * lineK
            bX = 2 * lineK * (lineB - circlePos[1]) - 2 * circlePos[0]
            cX = circlePos[0] * circlePos[0] + (lineB - circlePos[1]) * (lineB - circlePos[1]) - longRadiusSquare

            resultX = bX * bX - 4 * aX * cX
            x1 = (-bX + np.sqrt(resultX)) / (2 * aX)
            x2 = (-bX - np.sqrt(resultX)) / (2 * aX)

            y1 = lineK * x1 + lineB
            y2 = lineK * x2 + lineB

            if posInput[0] > circlePos[0]:
                if x1 > circlePos[0]:
                    xGenOut = x1 - outline
                    yGenOut = y1
                else:
                    xGenOut = x2 + outline
                    yGenOut = y2
            elif posInput[0] < circlePos[0]:
                if x1 < circlePos[0]:
                    xGenOut = x1 + outline
                    yGenOut = y1
                else:
                    xGenOut = x2 - outline
                    yGenOut = y2
            elif posInput[0] == circlePos[0]:
                if posInput[1] > circlePos[1]:
                    if y1 > circlePos[1]:
                        xGenOut = x1
                        yGenOut = y1 - outline
                    else:
                        xGenOut = x2
                        yGenOut = y2 + outline

            return xGenOut, yGenOut


def planeLinkageReverse(linkageLen, linkageEnDe, servoNum, debugPos, goalPos):  # E
    goalPos[0] = goalPos[0] + debugPos[0]
    goalPos[1] = goalPos[1] + debugPos[1]

    AngleEnD = np.arctan(linkageEnDe / linkageLen[1]) * 180 / np.pi

    linkageLenREAL = np.sqrt(((linkageLen[1] * linkageLen[1]) + (linkageEnDe * linkageEnDe)))

    goalPos[0], goalPos[1] = limitCheck(goalPos, debugPos, [linkageLen[0], linkageLenREAL], 0.00001)

    if goalPos[0] < 0:
        goalPos[0] = - goalPos[0]
        mGenOut = linkageLenREAL * linkageLenREAL - linkageLen[0] * linkageLen[0] - goalPos[0] * goalPos[0] - goalPos[
            1] * goalPos[1]
        nGenOut = mGenOut / (2 * linkageLen[0])

        angleGenA = np.arctan(goalPos[1] / goalPos[0]) + np.arcsin(
            nGenOut / np.sqrt(goalPos[0] * goalPos[0] + goalPos[1] * goalPos[1]))
        angleGenB = np.arcsin((goalPos[1] - linkageLen[0] * np.cos(angleGenA)) / linkageLenREAL) - angleGenA

        angleGenA = 90 - angleGenA * 180 / np.pi
        angleGenB = angleGenB * 180 / np.pi

        linkageLenC = np.sqrt((goalPos[0] * goalPos[0] + goalPos[1] * goalPos[1]))

        linkagePointC = np.arcsin(goalPos[0] / goalPos[1]) * 180 / np.pi * servoDirection[servoNumCtrl[0]]

        anglePosC = angleGenB + angleGenA

        return [angleGenA * servoDirection[servoNumCtrl[0]], (angleGenB + AngleEnD) * servoDirection[servoNumCtrl[1]],
                linkageLenC, linkagePointC, anglePosC]

    elif goalPos[0] == 0:
        angleGenA = np.arccos(
            (linkageLen[0] * linkageLen[0] + goalPos[1] * goalPos[1] - linkageLenREAL * linkageLenREAL) / (
                    2 * linkageLen[0] * goalPos[1]))
        cGenOut = np.tan(angleGenA) * linkageLen[0]
        dGenOut = goalPos[1] - (linkageLen[0] / np.cos(angleGenA))
        angleGenB = np.arccos(
            (cGenOut * cGenOut + linkageLenREAL * linkageLenREAL - dGenOut * dGenOut) / (2 * cGenOut * linkageLenREAL))

        angleGenA = - angleGenA * 180 / np.pi + 90
        angleGenB = - angleGenB * 180 / np.pi

        linkageLenC = np.sqrt((goalPos[0] * goalPos[0] + goalPos[1] * goalPos[1]))

        linkagePointC = angleGenB + 90 - angleGenA

        anglePosC = angleGenB + angleGenA

        return [angleGenA * servoDirection[servoNumCtrl[0]], (angleGenB + AngleEnD) * servoDirection[servoNumCtrl[1]],
                linkageLenC, linkagePointC, anglePosC]

    elif goalPos[0] > 0:
        sqrtGenOut = np.sqrt(goalPos[0] * goalPos[0] + goalPos[1] * goalPos[1])
        nGenOut = (linkageLen[0] * linkageLen[0] + goalPos[0] * goalPos[0] + goalPos[1] * goalPos[
            1] - linkageLenREAL * linkageLenREAL) / (2 * linkageLen[0] * sqrtGenOut)
        angleA = np.arccos(nGenOut) * 180 / np.pi

        AB = goalPos[1] / goalPos[0]

        angleB = np.arctan(AB) * 180 / np.pi
        angleGenA = angleB - angleA

        mGenOut = (linkageLen[0] * linkageLen[0] + linkageLenREAL * linkageLenREAL - goalPos[0] * goalPos[0] - goalPos[
            1] * goalPos[1]) / (2 * linkageLen[0] * linkageLenREAL)
        angleGenB = np.arccos(mGenOut) * 180 / np.pi - 90

        linkageLenC = np.sqrt((goalPos[0] * goalPos[0] + goalPos[1] * goalPos[1]))

        # linkagePointC = np.arcsin(goalPos[1]/goalPos[0])*180/np.pi*servoDirection[servoNumCtrl[0]]
        linkagePointC = 0

        anglePosC = angleGenB + angleGenA

        return [angleGenA * servoDirection[servoNumCtrl[0]], (angleGenB + AngleEnD) * servoDirection[servoNumCtrl[1]],
                linkageLenC, linkagePointC, anglePosC]


def planeLinkageDouble(linkageLen, goalPos):  # E
    goalPos[0], goalPos[1] = limitCheck(goalPos, [0, 0], [linkageLen, linkageLen], 0.00001)

    if goalPos[0] <= 0:
        # goalPos[0] = - goalPos[0]

        lineF = np.sqrt(goalPos[0] ** 2 + goalPos[1] ** 2)
        largeAng = np.arccos((lineF ** 2) / (2 * linkageLen * lineF)) * 180 / np.pi
        smallAng = np.arctan(goalPos[0] / goalPos[1]) * 180 / np.pi

        angleGenA = largeAng - smallAng
        # print(smallAng)
        return angleGenA
    elif goalPos[0] > 0:
        lineF = np.sqrt(goalPos[0] ** 2 + goalPos[1] ** 2)
        angL = np.arcsin(goalPos[0] / lineF) * 180 / np.pi
        angR = np.arccos((lineF ** 2) / (2 * linkageLen * lineF)) * 180 / np.pi
        angleGenA = angL + angR
        return angleGenA


def middlePosGenOut(linkageLen, angleInputA, angleInputB):
    angleInputA = -angleInputA
    angleV = 90 + angleInputB
    lineF = np.sqrt(
        -np.cos(angleV * np.pi / 180) * 2 * linkageLen[0] * linkageLen[1] + linkageLen[0] ** 2 + linkageLen[1] ** 2)
    angleO = np.arccos(
        (linkageLen[0] ** 2 + lineF ** 2 - linkageLen[1] ** 2) / (2 * linkageLen[0] * lineF)) * 180 / np.pi

    if angleO < angleInputA:
        angleU = (angleInputA - angleO) * np.pi / 180
        middleOutX = np.sin(angleU) * lineF
        middleOutY = np.cos(angleU) * lineF
        return [-middleOutX, middleOutY]
    # print(-middleOutX)
    if angleO > angleInputB:
        angleU = (angleO - angleInputA) * np.pi / 180
        middleOutX = np.sin(angleU) * lineF
        middleOutY = np.cos(angleU) * lineF
        return [middleOutX, -middleOutY]


def animateLine(xInput, yInput, lineLen, angleInput, debugInput):
    angleOri = angleInput
    debugOri = debugInput

    aOut = angleInput + debugInput

    angleLine = aOut

    if angleLine < -360:
        angleLine = (-angleLine - 360) * np.pi / 180
        xOut = np.cos(angleLine) * lineLen + xInput
        yOut = -np.sin(angleLine) * lineLen + yInput

    elif angleLine < -180 and angleLine >= -360:
        angleLine = (-angleLine - 180) * np.pi / 180
        xOut = xInput - np.cos(angleLine) * lineLen
        yOut = yInput + np.sin(angleLine) * lineLen

    elif angleLine >= -180 and angleLine < -90:
        angleLine = (180 + angleLine) * np.pi / 180
        xOut = xInput - np.cos(angleLine) * lineLen
        yOut = yInput - np.sin(angleLine) * lineLen

    elif angleLine <= 90 and angleLine >= -90:
        angleLine = angleLine * np.pi / 180
        xOut = np.cos(angleLine) * lineLen + xInput
        yOut = np.sin(angleLine) * lineLen + yInput

    elif angleLine > 90 and angleLine <= 180:
        angleLine = (180 - angleLine) * np.pi / 180
        xOut = xInput - np.cos(angleLine) * lineLen
        yOut = yInput + np.sin(angleLine) * lineLen

    elif angleLine > 180 and angleLine <= 360:
        angleLine = (angleLine - 180) * np.pi / 180
        xOut = xInput - np.cos(angleLine) * lineLen
        yOut = yInput - np.sin(angleLine) * lineLen

    elif angleLine > 360:
        angleLine = (angleLine - 360) * np.pi / 180
        xOut = np.cos(angleLine) * lineLen + xInput
        yOut = np.sin(angleLine) * lineLen + yInput

    else:
        print('Out of Range')

    return [[xInput, xOut], [yInput, yOut], aOut]


fig = plt.figure(tight_layout=True)

line_1, = plt.plot([], [], 'o-', lw=2)
line_2, = plt.plot([], [], 'o-', lw=2)
line_3, = plt.plot([], [], 'o-', lw=2)
line_4, = plt.plot([], [], 'o-', lw=2)

textPoint_A = plt.text(4, 0.8, '', fontsize=sizeFont)
textPoint_B = plt.text(4, 0.8, '', fontsize=sizeFont)
textPoint_C = plt.text(4, 0.8, '', fontsize=sizeFont)
textPoint_D = plt.text(4, 0.8, '', fontsize=sizeFont)
textPoint_M = plt.text(4, 0.8, '', fontsize=sizeFont)
textPoint_O = plt.text(4, 0.8, '', fontsize=sizeFont)

line_5, = plt.plot([], [], 'o-', lw=2)
line_6, = plt.plot([], [], 'o-', lw=2)


def animateII(i):
    if 0 <= i <= 20:
        InputX = 130 - i
        InputY = -40
    elif 20 < i <= 120:
        InputX = 110
        InputY = -60 + i
    elif 120 < i <= 140:
        InputX = 110 + i - 120
        InputY = 60
    elif 140 < i <= 240:
        InputX = 130
        InputY = 60 - i + 140
    # 以上部分被注释掉了
    a = planeLinkageReverse([linkageLenA, (linkageLenB + linkageLenC)], -linkageLenD, servoNumCtrl, [0, 0],
                            [70, -20 + i])

    [x1, y1, a1] = animateLine(0, 0, linkageLenA, a[0], -90)
    [x2, y2, a2] = animateLine(x1[1], y1[1], (linkageLenB + linkageLenC), a[1], a1 + 90)
    [x3, y3, a3] = animateLine(x2[1], y2[1], -linkageLenD, a2, 90)

    b = middlePosGenOut([linkageLenA, linkageLenB], -a1, a2)

    [x4, y4, a4] = animateLine(x1[1], y1[1], (linkageLenB), a[1], a1 + 90)

    line_1.set_data(x1, y1)
    line_2.set_data(x2, y2)
    line_3.set_data(x3, y3)
    line_4.set_data(x4, y4)

    textPoint_A.set_text("ang=%.1f" % (a[0]))
    textPoint_B.set_text("x=%.1f, y=%.1f , ang=%.1f" % (x1[1], y1[1], a[1] * servoDirection[servoNumCtrl[1]]))
    textPoint_C.set_text("x=%.1f, y=%.1f , angBase=%.1f" % (x2[1], y2[1], a2))
    textPoint_D.set_text("x=%.1f, y=%.1f , angBase=%.1f" % (x3[1], y3[1], a3))

    textPoint_M.set_text("x=%.1f, y=%.1f" % (x4[1], y4[1]))

    textPoint_A.set_position((-20, 5))
    textPoint_B.set_position((x1[1], y1[1]))
    textPoint_C.set_position((x2[1], y2[1]))
    textPoint_D.set_position((x3[1], y3[1]))
    textPoint_M.set_position((x4[1], y4[1]))

    c = planeLinkageDouble(linkageLenA, [(x4[1] - linkageLenE), y4[1]])

    [x5, y5, a5] = animateLine(linkageLenE, 0, linkageLenA, c, -90)

    textPoint_O.set_text("ang=%.1f" % c)
    textPoint_O.set_position((20, 5))

    line_5.set_data(x5, y5)
    line_6.set_data([x4[1], x5[1]], [y4[1], y5[1]])

    return line_1, line_2, line_3, line_4, line_5, line_6, textPoint_A, textPoint_B, textPoint_C, textPoint_D, textPoint_M, textPoint_O,


def initAnimate():
    line_1.set_data([], [])
    line_2.set_data([], [])
    return line_1, line_2,


plt.axis("equal")
plt.grid()
plt.grid(ls="--")
plt.xlim(-200, 200)
plt.ylim(-200, 200)

ani = animation.FuncAnimation(fig, animateII(10), 30,
                              interval=10, blit=True, init_func=initAnimate)  # frames:0-60

plt.show()
