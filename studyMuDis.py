import ROOT
import pickle
import os
import shipunit as u
import rootUtils as ut

if not os.uname()[1].find('ubuntu') < 0:
    path = '/media/Data/HNL/'
    sdir = {'disV': 'muVetoDIS', 'disCLBY': 'clbyDIS', 'disEM': 'muVetoEM'}
else:
    path = '/afs/cern.ch/project/lbcern/vol2/truf/'
    sdir = {'disV': 'muVDIS', 'disCLBY': 'clbyDIS', 'disEM': 'muVetoEM'}

sweights = {'disV': 1E4, 'disCLBY': 5 * 1E3, 'disEM': 1E3}


def makeFlist(prods, subdir):
    flist = []
    tmp = 'ship.10.0.muonDIS-TGeant4_Ana.pkl'
    for r in prods:
        for x in sdir:
            if x in r:
                subdir = path + sdir[x] + '/'
        for i in range(1, 10):
            theFile = subdir + r + str(i) + '/' + tmp
            if os.path.exists(theFile):
                flist.append(theFile)
    return flist


output = open('studyMuDis.out', 'w')
# get current dir
xx = os.path.abspath('.').split('/')
xx.reverse()
curdir = xx[0]

if 'clbyDIS' == curdir:
    prods = ['disCLBY0', 'disCLBY1', 'disCLBY2', 'disCLBY3']
    subdir = 'disCLBY'
elif 'muVetoDIS' == curdir:
    prods = ['disV50', 'disV60', 'disV70', 'disV80']
    subdir = 'disV'
elif 'muVDIS' == curdir:
    prods = [
        'disV150', 'disV160', 'disV170', 'disV180', 'disV50', 'disV60',
        'disV70', 'disV80'
    ]
    subdir = 'disV'
elif 'muVetoEM' == curdir:
    prods = ['disEM4', 'disEM5', 'disEM6', 'disEM7', 'disEM8', 'disEM9']
    subdir = 'disEM'
else:
    prods = [
        'disV50', 'disV60', 'disV70', 'disV80', 'disCLBY0', 'disCLBY1',
        'disCLBY2', 'disCLBY3'
    ]
    # prods=['disV50']
    subdir = 'disV'
first = True
sweights = {'disV': 1E4, 'disCLBY': 5 * 1E3, 'disEM': 1E3}
geoFile = path + sdir[subdir] + '/' + prods[0] + \
    '1/geofile_full.10.0.muonDIS-TGeant4.root'

flist = makeFlist(prods, subdir)

fgeo = ROOT.TFile(geoFile)
sGeo = fgeo.FAIRGeom
from ShipGeoConfig import ConfigRegistry
ecalGeoFile = 'ecal_ellipse5x10m2.geo'
ShipGeo = ConfigRegistry.loadpy(
    '$FAIRSHIP/geometry/geometry_config.py', EcalGeoFile=ecalGeoFile)

bfield = ROOT.genfit.BellField(ShipGeo.Bfield.max, ShipGeo.Bfield.z, 2,
                               ShipGeo.Yheight / 2. * u.m)
fM = ROOT.genfit.FieldManager.getInstance()
fM.init(bfield)

geoMat = ROOT.genfit.TGeoMaterialInterface()
ROOT.genfit.MaterialEffects.getInstance().init(geoMat)

h = {}

# prepare veto decisions
import shipVeto
veto = shipVeto.Task()
# fiducial cuts
vetoStation = ROOT.gGeoManager.GetTopVolume().GetNode('Veto_5')
vetoStation_zDown = vetoStation.GetMatrix().GetTranslation()[
    2] + vetoStation.GetVolume().GetShape().GetDZ() + 5 * u.cm
T1Station = ROOT.gGeoManager.GetTopVolume().GetNode('Tr1_1')
T1Station_zUp = T1Station.GetMatrix().GetTranslation()[
    2] - T1Station.GetVolume().GetShape().GetDZ() - 5 * u.cm
dy = 10.
V0dict = {130: 'KL', 310: 'KS', 3122: 'Lambda', 321: 'K+', 22: 'gamma'}
reV0dict = {}
for x in V0dict:
    reV0dict[V0dict[x]] = x
vetoDets = {
    'UVT': (False, 0),
    'SVT': (False, 0),
    'SBT': (False, 0),
    'RPC': (False, 0),
    'TRA': (False, 0)
}

statistics = {'All': [0, 0, 0, 0]}
for v0 in V0dict:
    statistics[v0] = [0, 0, 0, 0]
statistics[-1] = [0, 0, 0, 0]
for x in ['', '-inMu', '+inMu']:
    for vt in vetoDets:
        statistics[vt + x] = [0, 0, 0, 0]
    z = 'SVT&UVT&SBT'
    statistics[z + x] = [0, 0, 0, 0]
    z = 'SVT&UVT&SBT&RPC'
    statistics[z + x] = [0, 0, 0, 0]


def update(x, cand):
    statistics[x][0] += cand['All']
    statistics[x][1] += cand['IP<2.5m']
    statistics[x][2] += cand['IP<0.1m']
    statistics[x][3] += cand['M<2GeV']


def Rsq(X, Y, dy):
    return (X / (2.45 * u.m))**2 + (Y / ((dy / 2. - 0.05) * u.m))**2


def analyzeWeights():
    first = True
    for f in flist:
        fp = open(f)
        for x in sdir:
            if x in f:
                # how often a muon was re-used to make an interaction
                sweight = sweights[x]
        if first:
            first = False
            weightsUsed = pickle.load(fp)
            for wkey in weightsUsed:
                weightsUsed[wkey].append(sweight)
                weightsUsed[wkey].append(1)
        else:
            temp = pickle.load(fp)
            for wkey in temp:
                if wkey not in weightsUsed:
                    weightsUsed[wkey] = [0, 0, 0, 0]
                weightsUsed[wkey][0] += temp[wkey][0]
                weightsUsed[wkey][1] += temp[wkey][1]
                weightsUsed[wkey][2] += sweight
                weightsUsed[wkey][3] += 1
    print 'Analysis of weights'
    #   weightsUsed[wkey][0]+= Nexptected # sum of expected muon interactions
    # weightsUsed[wkey][1]+= 1.         # counts how often a muon weight had
    # been used
    print 'weight    sum of weights  sum of entries     mean'
    pot = []
    for wkey in weightsUsed:
        mean = weightsUsed[wkey][0] / weightsUsed[wkey][1]
        print wkey, weightsUsed[wkey], mean
        # print "corresponding pot: %10.2G"%(2E15/wkey/mean*1E4*60) # ???
        # discovered 5 August, why 2E15? should be 5E13!!!
        print 'different re-use of muon taken into account [2]/[3] * len(prods)'
        print 'corresponding pot: %10.2G * number of iterations(2*30) * 2(like sign) * %2i (nprod) * %10.2G (reuse of mu)'\
            % (5E13 / wkey / mean, len(prods), weightsUsed[wkey][2] / weightsUsed[wkey][3])
        N = 5E13 / wkey / mean * \
            weightsUsed[wkey][2] / weightsUsed[wkey][3] * 60 * 2 * len(prods)
        pot.append(N)
        # 60 == 30 x CERN+Yandex statistics,  2 like sign
        print ' == %10.2G' % (N)
    pot.sort()
    # try to estimate muon interactions for 2E20 pot:
    for wkey in weightsUsed:
        sumOfWeights = weightsUsed[wkey][0]
        muReuse = weightsUsed[wkey][2] / weightsUsed[wkey][3]
        muInter = sumOfWeights * wkey * \
            (2E20 / 5E13) / (muReuse * 60 * len(prods))
        print 'muon interactions for key: %i %10.2G ' % (wkey, muInter)
    return pot[0]


#
interestingEvents = {}
final = {}


def studyBackground():
    counters = {
        'All': 0,
        'NTrack=2': 0,
        'NTrack=3': 0,
        'NTrack>3': 0,
        'RPCVeto': 0
    }
    for v0 in V0dict:
        counters[v0] = 0
    counters[-1] = 0
    #
    for f in flist:
        fp = open(f)
        weightsUsed = pickle.load(fp)
        bckg = pickle.load(fp)
        fp.close()
        inputFile = f.replace('Ana', 'rec').replace('pkl', 'root')
        tmp = os.path.realpath(inputFile)
        if not tmp.find('eos') < 0:
            eospath = 'root://eoslhcb/' + tmp.split('truf')[1]
            ft = ROOT.TFile.Open(eospath)
        else:
            ft = ROOT.TFile(inputFile)
        sTree = ft.cbmsim
        output.write('==> input file %s \n' % (f))
        output.write(
            'evt nr  candidate startZ    volName    muonPZ  weight    Doca   IP     Mass   nr tracks    RPC# conv P>1 \n'
        )
        interestingEvents[f] = []
        for nb in bckg:
            sTree.GetEvent(nb)
            vetoDets['TRA'] = veto.Track_decision(sTree)
            #
            mu = sTree.MCTrack[0]
            nd = ROOT.gGeoManager.FindNode(mu.GetStartX(),
                                           mu.GetStartY(), mu.GetStartZ())
            vetoDets['SBT'] = veto.SBT_decision(sTree)
            vetoDets['SVT'] = veto.SVT_decision(sTree)
            vetoDets['UVT'] = veto.UVT_decision(sTree)
            vetoDets['RPC'] = veto.RPC_decision(sTree)
            #  MCTrack[1] = incoming muon
            vetoDets['SBT+inMu'] = veto.SBT_decision(sTree, 1)
            vetoDets['SVT+inMu'] = veto.SVT_decision(sTree, 1)
            vetoDets['UVT+inMu'] = veto.UVT_decision(sTree, 1)
            vetoDets['RPC+inMu'] = veto.RPC_decision(sTree, 1)
            vetoDets['SBT-inMu'] = veto.SBT_decision(sTree, -1)
            vetoDets['SVT-inMu'] = veto.SVT_decision(sTree, -1)
            vetoDets['UVT-inMu'] = veto.UVT_decision(sTree, -1)
            vetoDets['RPC-inMu'] = veto.RPC_decision(sTree, -1)
            #
            counters['All'] += 1
            nm = nd.GetName()
            if nm not in counters:
                counters[nm] = 0
            counters[nm] += 1
            if vetoDets['TRA'][2] == 2:
                counters['NTrack=2'] += 1
            elif vetoDets['TRA'][2] == 3:
                counters['NTrack=3'] += 1
            elif vetoDets['TRA'][2] > 3:
                counters['NTrack>3'] += 1
            if vetoDets['RPC'][2] > 0:
                counters['RPCVeto'] += 1
            found = False
            b = sTree.Particles[bckg[nb][0]]
            t1, t2 = sTree.fitTrack2MC[b.GetDaughter(0)], sTree.fitTrack2MC[
                b.GetDaughter(1)]
            mc1, mc2 = sTree.MCTrack[t1].GetMotherId(), sTree.MCTrack[
                t2].GetMotherId()
            pc1, pc2 = abs(sTree.MCTrack[mc1].GetPdgCode()), abs(
                sTree.MCTrack[mc2].GetPdgCode())
            if (pc1 in V0dict or pc2 in V0dict) and pc1 == pc2:
                found = True
                output.write(
                    '%8i %8i %6.2F %12s %6.3F %6.3F %6.2F %6.2F %6.3F %4i %4i %4i \n'
                    % (nb, bckg[nb][0], mu.GetStartZ() / u.m,
                       nd.GetName().split('_')[0], mu.GetPz() / u.GeV,
                       bckg[nb][4], bckg[nb][1] / u.cm, bckg[nb][2] / u.cm,
                       bckg[nb][3] / u.GeV, pc1, bckg[nb][8],
                       sTree.FitTracks.GetEntries()))
                if bckg[nb][3] / u.GeV > 0.55:
                    interestingEvents[f].append(nb)
            if not found:
                pc1 = -1
                output.write(
                    '%8i %8i %6.2F %12s %6.3F %6.3F %6.2F %6.2F %6.3F %4i %4i %4i \n'
                    % (nb, bckg[nb][0], mu.GetStartZ() / u.m,
                       nd.GetName().split('_')[0], mu.GetPz() / u.GeV,
                       bckg[nb][4], bckg[nb][1] / u.cm, bckg[nb][2] / u.cm,
                       bckg[nb][3] / u.GeV, pc1, bckg[nb][8],
                       sTree.FitTracks.GetEntries()))
#
#  all  IP<2.5m   IP<0.1m   M<2GeV
            cand = {'All': 1, 'IP<2.5m': 0, 'IP<0.1m': 0, 'M<2GeV': 0}
            if bckg[nb][2] / u.cm < 250.:
                cand['IP<2.5m'] = 1
            if bckg[nb][2] / u.cm < 10.:
                cand['IP<0.1m'] = 1
            if bckg[nb][3] / u.GeV < 2. and bckg[nb][2] / u.cm < 10.:
                cand['M<2GeV'] = 1
            update('All', cand)
            update(pc1, cand)
            vt = 'TRA'
            if not vetoDets[vt][0]:
                update(vt, cand)
                continue
#
            for vt in vetoDets:
                if not vetoDets[vt][0]:
                    update(vt, cand)
            for x in ['', '-inMu', '+inMu']:
                if not vetoDets['SBT' +
                                x] and not vetoDets['SVT' +
                                                    x] and not vetoDets['UVT' +
                                                                        x]:
                    update('SVT&UVT&SBT' + x, cand)
                    if not vetoDets['RPC' + x]:
                        update('SVT&UVT&SBT&RPC' + x, cand)
            counters[pc1] += 1
            #
            tmp = ''
            for x in vetoDets:
                tmp += x + ':'
                for y in vetoDets[x]:
                    tmp += str(y) + ' '
            output.write(tmp)
            output.write('\n')
    counters['volIron'] = 0
    counters['volRpc'] = 0
    counters['volHPT'] = 0
    counters['T1Li'] = 0
    counters['T1'] = 0
    counters['strawVeto'] = 0
    for s in counters:
        if not isinstance(s, type('s')):
            continue
        if not s.find('volIron_') < 0:
            counters['volIron'] += counters[s]
        if not s.find('volRpc_') < 0:
            counters['volRpc'] += counters[s]
        if not s.find('volHPT_') < 0:
            counters['volHPT'] += counters[s]
        if not s.find('T1LiSc') < 0:
            counters['T1Li'] += counters[s]
        if not s.find('T1Rib') < 0 or not s.find('T1Lid') < 0:
            counters['T1'] += counters[s]
        if not s.find('straw') < 0 or not s.find('gas') < 0:
            counters['strawVeto'] += counters[s]
    for x in counters:
        sx = x
        if isinstance(x, type(1)):
            sx = str(x)
        tmp = sx + ':' + str(counters[x]) + '\n'
        output.write(tmp)
# make nice statistics corresponding to 2E20, numbers are for ~5E20 not
# anymore, 2.5E19
    scale = 2.E20 / analyzeWeights()
    # do by hand, use all big productions 50,60,70,80,150,160,170,180 --> 1E20
    if subdir == 'disV':
        scale = 2.E20 / 1.E20
    if subdir == 'disEM':
        scale = 2.E20 / 1.5E15  # = 5E13/24000.*60*2*6*1000
    for x in statistics:
        final[x] = {}
        for i in range(len(statistics[x])):
            if statistics[x][i] == 0:
                final[x][i] = '<%3.1F' % (2.3 * scale)
            else:
                final[x][i] = '%4.1F' % (statistics[x][i] * scale)

    output.write(' Scale factor used: ' + str(scale))
    output.write(
        '          Selection  & Number of candidates   &  $IP<2.5\,$m &  $IP<10\,$cm  \\\\ \n'
    )
    output.write(' \hline\n')
    z = 'All (\# tracks$<5$) '
    vt = 'All'
    xx = '%20s       &     $ %6s $   &  $  %6s $  &  $  %5s $  \\\\ \n'
    output.write(xx % (z, final[vt][0], final[vt][1], final[vt][2]))
    #
    V0tex = {
        'K+': 'from $K^+$',
        'KS': 'from $K_S$',
        'Lambda': 'from $\Lambda$',
        'KL': 'from $K_L$',
        'gamma': 'from conv $\gamma$'
    }
    for v0 in ['K+', 'KS', 'Lambda', 'KL', 'gamma']:
        z = reV0dict[v0]
        output.write(xx % (V0tex[v0], final[z][0], final[z][1], final[z][2]))
    #z = 'TRA'
    #output.write(xx%(z,final[z][0],final[z][1],final[z][2],final[z][3]) )
    output.write(' \hline\n')
    output.write(' \multicolumn{4}{c}{\# tracks $=2$}\\\\ \n')
    x = ''
    for vt in ['SBT', 'RPC', 'UVT', 'SVT', 'SVT&UVT&SBT', 'SVT&UVT&SBT&RPC']:
        z = 'passing ' + vt.replace('&', '\&')
        output.write(xx % (z, final[vt][0], final[vt][1], final[vt][2]))
    output.write(' \hline\n')
    output.write(
        ' \multicolumn{4}{c}{using only Veto information of incoming muon}\\\\ \n'
    )
    x = '+inMu'
    for vt in ['SBT', 'RPC', 'UVT', 'SVT', 'SVT&UVT&SBT', 'SVT&UVT&SBT&RPC']:
        z = 'passing ' + vt.replace('&', '\&')
        output.write(xx %
                     (z, final[vt + x][0], final[vt + x][1], final[vt + x][2]))
    output.write(' \hline\n')
    output.write(
        ' \multicolumn{4}{c}{using only Veto information from particles produced in muon interaction}\\\\ \n'
    )
    x = '-inMu'
    for vt in ['SBT', 'RPC', 'UVT', 'SVT', 'SVT&UVT&SBT', 'SVT&UVT&SBT&RPC']:
        z = 'passing ' + vt.replace('&', '\&')
        output.write(xx %
                     (z, final[vt + x][0], final[vt + x][1], final[vt + x][2]))

#
    for x in interestingEvents:
        if len(interestingEvents[x]) > 0:
            tmp = ''
            for i in interestingEvents[x]:
                tmp += str(i) + ','
            output.write('%s %s \n' % (x, tmp))


def studyV0():
    counters = {}
    for x in V0dict:
        counters[x] = {}
        for v in vetoDets:
            counters[x][v] = 0
    for f in flist:
        fp = open(f)
        weightsUsed = pickle.load(fp)
        bckg = pickle.load(fp)
        fp.close()
        inputFile = f.replace('Ana', 'rec').replace('pkl', 'root')
        tmp = os.path.realpath(inputFile)
        if not tmp.find('eos') < 0:
            eospath = 'root://eoslhcb/' + tmp.split('truf')[1]
            ft = ROOT.TFile.Open(eospath)
        else:
            ft = ROOT.TFile(inputFile)
        sTree = ft.cbmsim
        print '==> input file ', f
        for nb in bckg:
            v0 = bckg[nb][8]
            if v0 not in V0dict:
                continue
            sTree.GetEvent(nb)
            vetoDets['SBT'], w = veto.SBT_decision(sTree)
            vetoDets['SVT'], w = veto.SVT_decision(sTree)
            vetoDets['UVT'], w = veto.UVT_decision(sTree)
            vetoDets['RPC'], w = veto.RPC_decision(sTree)
            vetoDets['TRA'], w = veto.Track_decision(sTree)
            for v in vetoDets:
                if not vetoDets[v]:
                    counters[v0][v] += 1
#
    for v in vetoDets:
        print 'veto detector ', v
        for v0 in counters:
            print V0dict[v0], ':', counters[v0][v]


#


def studyNoV0():
    counters = {}
    for v in vetoDets:
        ut.bookHist(h, 'Vz' + v, 'z position of vertex [m] ' + v, 1000, -30.,
                    50.)
    ut.bookHist(h, 'oa', 'cos opening angle', 100, 0.999, 1.)
    for f in flist:
        fp = open(f)
        weightsUsed = pickle.load(fp)
        bckg = pickle.load(fp)
        fp.close()
        inputFile = f.replace('Ana', 'rec').replace('pkl', 'root')
        ft = ROOT.TFile(inputFile)
        sTree = ft.cbmsim
        print '==> input file ', f
        for nb in bckg:
            v0 = bckg[nb][8]
            if v0 in V0dict:
                continue
            sTree.GetEvent(nb)
            vetoDets['SBT'], w = veto.SBT_decision(sTree)
            vetoDets['SVT'], w = veto.SVT_decision(sTree)
            vetoDets['UVT'], w = veto.UVT_decision(sTree)
            vetoDets['RPC'], w = veto.RPC_decision(sTree)
            vetoDets['TRA'], w = veto.Track_decision(sTree)
            p = sTree.Particles[bckg[nb][0]]
            HNLPos = ROOT.TLorentzVector()
            p.ProductionVertex(HNLPos)
            xv, yv, zv, doca = HNLPos.X() / u.m, HNLPos.Y() / \
                u.m, HNLPos.Z() / u.m, HNLPos.T() / u.cm
            for v in vetoDets:
                if not vetoDets[v]:
                    h['Vz' + v].Fill(zv)
                    print 'no V0:', nb, bckg[nb][0], zv, ROOT.TMath.Sqrt(
                        xv * xv + yv * yv), v
            newPos = ROOT.TVector3(xv, yv, zv)
            t1, t2 = sTree.FitTracks[p.GetDaughter(0)].getFittedState(
            ), sTree.FitTracks[p.GetDaughter(1)].getFittedState()
            rep1, rep2 = ROOT.genfit.RKTrackRep(
                t1.getPDG()), ROOT.genfit.RKTrackRep(t2.getPDG())
            state1, state2 = ROOT.genfit.StateOnPlane(
                rep1), ROOT.genfit.StateOnPlane(rep2)
            rep1.setPosMom(state1, t1.getPos(), t1.getMom())
            rep2.setPosMom(state2, t2.getPos(), t2.getMom())
            try:
                rep1.extrapolateToPoint(state1, newPos, False)
                rep2.extrapolateToPoint(state2, newPos, False)
                mom1, mom2 = rep1.getMom(state1), rep2.getMom(state2)
            except BaseException:
                print 'extrapolation failed. take stored state'
                mom1, mom2 = t1.getMom(), t2.getMom()
            oa = mom1.Dot(mom2) / (mom1.Mag() * mom2.Mag())
            h['oa'].Fill(oa)


#

print 'studyBackground() for printout of background events.'
print 'studyV0() search for V0 events'
print 'studyNoV0()'
print 'analyzeWeights()'
