#!/bin/env python2
import click
import ROOT as r
from rootpy.io import root_open
import shipunit as u


@click.command()
@click.argument('inputfile')
@click.argument('geofile')
@click.option('-o', '--output', default='test.root')
def makeMuonInelasticTuple(inputfile, output, geofile):
    fout = r.TFile.Open(output, 'recreate')
    ntuple = r.TNtuple('muons', 'muon flux VetoCounter', 'id:px:py:pz:x:y:z:w')
    logVols = detMap(geofile)
    f = r.TFile.Open(inputfile)
    tree = f.cbmsim
    for event in tree:
        weight = (event.MCTrack[1].GetWeight()
                  if event.MCTrack.GetEntries() > 1
                  else event.MCTrack[0].GetWeight())
        for hit in event.vetoPoint:
            detID = hit.GetDetectorID()
            if logVols[detID] != 'cave':
                print logVols[detID]
                continue
            pid = hit.PdgCode()
            if abs(pid) != 13:
                continue
            P = r.TMath.Sqrt(hit.GetPx()**2 + hit.GetPy()**2 + hit.GetPz()**2)
            if P > 3 / u.GeV:
                ntuple.Fill(
                    float(pid),
                    float(hit.GetPx() / u.GeV),
                    float(hit.GetPy() / u.GeV),
                    float(hit.GetPz() / u.GeV),
                    float(hit.GetX() / u.m),
                    float(hit.GetY() / u.m),
                    float(hit.GetZ() / u.m), float(weight))
    fout.cd()
    ntuple.Write()


def detMap(geofile):
    with root_open(geofile) as fgeo:
        sGeo = fgeo.FAIRGeom
        detList = {}
        volList = sGeo.GetListOfVolumes()
        for v in volList:
            nm = v.GetName()
            i = sGeo.FindVolumeFast(nm).GetNumber()
            detList[i] = nm
        return detList


if __name__ == '__main__':
    makeMuonInelasticTuple()
