import argparse

import matplotlib as mpl
# mpl.use('Agg')

import matplotlib.style as style
style.use('bmh')

import matplotlib.pyplot as plt
from matplotlib import rcParams
rcParams['pdf.fonttype'] = 42
rcParams['ps.fonttype'] = 42
import numpy as np

from matplotlib import rc
rc('text', usetex=True)

########################################
# parameters

Von = 1.233
Voff = 0.9952 

p = 0.05

Esense = 10e-3

commPacketCapSize = 900e-3
commPacketEnergy = 0.5 * commPacketCapSize * (Von ** 2 - Voff ** 2)
commPacketSize = 8
commImageSize = 28 * 28 * 1
commImagePackets = 1. * commImageSize / commPacketSize
EcommImage = commPacketEnergy * commImagePackets

commResultSize = 8 # single packet
commResultPackets = 1. * commResultSize / commPacketSize
EcommResult = commPacketEnergy * commResultPackets

def setEcomm(commPackets):
    global EcommImage
    EcommImage = commPacketEnergy * commPackets

inferCapSize = 1e-3
inferCapDischarges = 100 # 4 for SVM
Einfer = inferCapDischarges * 0.5 * inferCapSize * (Von ** 2 - Voff ** 2)

inferOps = 6e5
def opsToEinfer(ops):
    return np.array(ops) * Einfer / inferOps

print('Sensing costs:', Esense)
print('Communication costs (image):', EcommImage)
print('Communication costs (result):', EcommResult)
print('Inference costs:', Einfer)

########################################
# model equations

def baseline(accuracy):
    return p / (Esense + EcommImage)

def idealImage(accuracy):
    return p / (Esense + p * EcommImage)

def naiveImage(accuracy):
    # return p / (Esense + Einfer + p * EcommImage)
    discharges = 749
    EnergyInfer = discharges * 0.5 * inferCapSize * (Von ** 2 - Voff ** 2)
    return p * accuracy / (Esense + EnergyInfer + ((p * accuracy) + (1-p) * (1-accuracy)) * EcommImage)

def sonicImage(accuracy):
    return p * accuracy / (Esense + Einfer + ((p * accuracy) + (1-p) * (1-accuracy)) * EcommImage)

def idealResult(accuracy):
    return p / (Esense + p * EcommResult)

def naiveResult(accuracy):
    # return p / (Esense + Einfer + p * EcommResult)
    global inferCapSize
    discharges = 749
    EnergyInfer = discharges * 0.5 * inferCapSize * (Von ** 2 - Voff ** 2)
    return p * accuracy / (Esense + EnergyInfer + ((p * accuracy) + (1-p) * (1-accuracy)) * EcommResult)

def sonicResult(accuracy):
    return p * accuracy / (Esense + Einfer + ((p * accuracy) + (1-p) * (1-accuracy)) * EcommResult)

def sonicDetailed(ops, truepositive, truenegative):
    return p * np.array(truepositive) / (Esense + opsToEinfer(ops) + (p * np.array(truepositive) + (1-p) * (1-np.array(truenegative))) * EcommImage)

if __name__ == "__main__":
    x = [0.88, 0.9865, 1]
    print('Sonic-Image / Always-Send-Image at', x, 'accuracy:', sonicImage(np.array(x)) / baseline(1))
    print('Sonic-Image / Naive-Image at', x, 'accuracy:', sonicImage(np.array(x)) / naiveImage(1))
    print('Sonic-Image / Ideal-Image at', x, 'accuracy:', sonicImage(np.array(x)) / idealImage(1))
    print('Sonic-Result / Always-Send-Image at', x, 'accuracy:', sonicResult(np.array(x)) / baseline(1))
    print('Sonic-Result / Naive-Result at', x, 'accuracy:', sonicResult(np.array(x)) / naiveResult(1))
    print('Sonic-Result / Ideal-Result at', x, 'accuracy:', sonicResult(np.array(x)) / idealResult(1))

x = np.linspace(0, 1, 100)
def transform(y):
    return np.zeros_like(x) + y

########################################
# wouldn't it be great if numpy supported braces natively?

def brace():
    def half_brace(x, beta):
        x0, x1 = x[0], x[-1]
        y = 1/(1.+np.exp(-1*beta*(x-x0))) + 1/(1.+np.exp(-1*beta*(x-x1)))
        return y
    xmax, xstep = 1, .005
    xaxis = np.arange(0, xmax, xstep)
    y0 = half_brace(xaxis[:len(xaxis)//2], 100.)
    y = np.concatenate((y0, y0[::-1]))
    y -= 0.5
    return xaxis, y
br = brace()

########################################
# wouldn't it be great if numpy supported sig figs natively?

def sigfigs(x, n):
    print(x, )
    i = 0
    while x > 10. ** n:
        x /= 10.
        i += 1
    while x < 10. ** (n-1):
        x *= 10.
        i -= 1
    x = int(x + 0.5)
    x *= 10 ** i
    print(x)
    return x

def plots(args):
    ########################################
    # send images plot

    def plotBrace(y0, y1, padding=0):
        xs = 1.02 + 0.05 * br[1] + padding
        # xs = [1.02 + 0.05 * br[1][0]] + xs.tolist() + [1.02 + 0.05 * br[1][-1]]
        ys = 1e3 * (br[0]*(y1 - y0) + y0)
        # ys = [1e3 * (br[0][0]*(y1 - y0) + y0)] + ys.tolist() + [1e3 * (br[0][-1]*(y1 - y0) + y0)]
        plt.plot(xs, ys,
                 clip_on=False, color='grey', lw=1) # , transform=fig.gca().transAxes)
        plt.text(1.08 + padding, 1e3 * (y1 + y0) / 2, ('%s' % sigfigs(y1 / y0, 2)) + r'$\times$',
                 color='grey', fontsize=11, ha = 'left', va = 'center')

    ########################################
    # send results only plot

    fig = plt.figure(figsize=(6.5,4))
    plt.plot(x, 1e3 * transform(baseline(x)), label='Always send image')
    plt.plot(x, 1e3 * transform(idealResult(x)), label=r'Ideal (send result only)', ls='--')
    plt.plot(x, 1e3 * transform(sonicResult(x)), label='Local inference')
    plotBrace(sonicResult(1.), round(idealResult(1.), 2), padding=0)
    plotBrace(baseline(1.), round(sonicResult(1.), 2), padding=0)
    plt.ylabel(r'Interesting \textit{results} sent' + '\nper harvested kilo-Joule')
    plt.xlabel('Accuracy')
    plt.xlim(0,1)
    plt.legend(loc='lower center', bbox_to_anchor=[0,1.02,1,1.1], ncol=3, columnspacing=1.5, handletextpad=0.25, fontsize=12)
    plt.tight_layout()
    if args.dest: plt.savefig(args.dest + '_results.pdf')
    # plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--dest',
        type=str,
        help='Destination file')
    args = parser.parse_args()
    plots(args)
