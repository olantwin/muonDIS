#!/bin/env python2
import sys
import time
from array import array
import ROOT  as r
# import click
nJob = 2
nMult = 10  # number of events / muon
muonIn = 'test.root'
nPerJob = 100

if len(sys.argv) > 1:
    nJob = int(sys.argv[1])
if len(sys.argv) > 2:
    nMult = int(sys.argv[2])
if len(sys.argv) > 3:
    muonIn = sys.argv[3]
if len(sys.argv) > 4:
    nPerJob = int(sys.argv[4])

PDG = r.TDatabasePDG.Instance()
masssq = {}


def getMasssq(pid):
    apid = abs(int(pid))
    if apid not in masssq:
        masssq[apid] = PDG.GetParticle(apid).Mass()**2
    return masssq[apid]


def rotate(ctheta, stheta, cphi, sphi, px, py, pz):
    # rotate around y-axis
    px1 = ctheta * px + stheta * pz
    pzr = -stheta * px + ctheta * pz
    # rotate around z-axis
    pxr = cphi * px1 - sphi * py
    pyr = sphi * px1 + cphi * py
    return pxr, pyr, pzr


def main():
    myPythia = r.TPythia6()
    myPythia.SetMSEL(2)  # msel 2 includes diffractive parts
    myPythia.SetPARP(2, 2)  # To get below 10 GeV, you have to change PARP(2)
    for kf in [211, 321, 130, 310, 3122, 3112, 3312]:
        kc = myPythia.Pycomp(kf)
        myPythia.SetMDCY(kc, 1, 0)

    R = int(time.time() % 900000000)
    myPythia.SetMRPY(1, R)
    mutype = {-13: 'gamma/mu+', 13: 'gamma/mu-'}

    # DIS event
    # incoming muon,      id:px:py:pz:x:y:z:w
    # outgoing particles, id:px:py:pz
    fout = r.TFile('muonDis_' + str(nJob) + '.root', 'recreate')
    dTree = r.TTree('DIS', 'muon DIS')
    iMuon = r.TClonesArray('TVectorD')
    iMuonBranch = dTree.Branch('InMuon', iMuon, 32000, -1)
    dPart = r.TClonesArray('TVectorD')
    dPartBranch = dTree.Branch('Particles', dPart, 32000, -1)

    # read file with muons hitting concrete wall
    fin = r.TFile(muonIn)  # id:px:py:pz:x:y:z:w
    sTree = fin.muons

    nTOT = sTree.GetEntries()

    nStart = nPerJob * nJob
    nEnd = min(nTOT, nStart + nPerJob)
    # if muonIn.find('Concrete') < 0:
    #     nStart = 0
    #     nEnd = nTOT

    # stop pythia printout during loop
    myPythia.SetMSTU(11, 11)
    print 'start production ', nStart, nEnd
    nMade = 0
    for k in range(nStart, nEnd):
        rc = sTree.GetEvent(k)
        # make n events / muon
        px, py, pz = sTree.px, sTree.py, sTree.pz
        x, y, z = sTree.x, sTree.y, sTree.z
        pid, w = sTree.id, sTree.w
        p = r.TMath.Sqrt(px * px + py * py + pz * pz)
        E = r.TMath.Sqrt(getMasssq(pid) + p * p)
        # px=p*sin(theta)cos(phi),py=p*sin(theta)sin(phi),pz=p*cos(theta)
        theta = r.TMath.ACos(pz / p)
        phi = r.TMath.ATan2(py, px)
        ctheta, stheta = r.TMath.Cos(theta), r.TMath.Sin(theta)
        cphi, sphi = r.TMath.Cos(phi), r.TMath.Sin(phi)
        mu = array('d', [pid, px, py, pz, E, x, y, z, w])
        muPart = r.TVectorD(9, mu)
        myPythia.Initialize('FIXT', mutype[pid], 'p+', p)
        for _ in range(nMult):
            dPart.Clear()
            iMuon.Clear()
            iMuon[0] = muPart
            myPythia.GenerateEvent()
            # remove all unnecessary stuff
            myPythia.Pyedit(2)
            for itrk in range(1, myPythia.GetN() + 1):
                did = myPythia.GetK(itrk, 2)
                dpx, dpy, dpz = rotate(ctheta, stheta, cphi, sphi,
                                       myPythia.GetP(itrk, 1),
                                       myPythia.GetP(itrk, 2),
                                       myPythia.GetP(itrk, 3))
                psq = dpx**2 + dpy**2 + dpz**2
                E = r.TMath.Sqrt(getMasssq(did) + psq)
                m = array('d', [did, dpx, dpy, dpz, E])
                part = r.TVectorD(5, m)
                # copy to branch
                nPart = dPart.GetEntries()
                if dPart.GetSize() == nPart:
                    dPart.Expand(nPart + 10)
                dPart[nPart] = part
            nMade += 1
            if nMade % 10000 == 0:
                print 'made so far ', nMade
            dTree.Fill()
    fout.cd()
    dTree.Write()
    myPythia.SetMSTU(11, 6)
    print 'created nJob ', nJob, ':', nStart, ' - ', nEnd, ' events'


if __name__ == '__main__':
    main()
