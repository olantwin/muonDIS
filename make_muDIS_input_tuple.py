#!/bin/env python2
import click
import ROOT as r
from rootpy.io import root_open
import shipunit as u


@click.command()
@click.argument('inputfile')
@click.argument('geofile')
@click.option('-o', '--output', default='test.root')
@click.option('-v', '--volume', default='rockD')
def makeMuonInelasticTuple(inputfile, output, geofile, volume):
    fout = r.TFile.Open(output, 'recreate')
    ntuple = r.TNtuple('muons', 'muon flux concrete', 'id:px:py:pz:x:y:z:w')
    f = r.TFile.Open(inputfile)
    tree = f.cbmsim
    for event in tree:
        weight = (event.MCTrack[1].GetWeight()
                  if event.MCTrack.GetEntries() > 1
                  else event.MCTrack[0].GetWeight())
        for hit in event.vetoPoint:
            detID=hit.GetDetectorID()
            if detID>10000:
                continue
            node=r.gGeoManager.FindNode(hit.GetX(),hit.GetY(),hit.GetZ())
            if not volume in node.GetName():
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


if __name__ = '__main__':
    makeMuonInelasticTuple()
                                                                                                                     47,17         Bot

