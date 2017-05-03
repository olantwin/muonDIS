#!/bin/env python2
import click
import numpy as np
import ROOT as r
from rootpy.io import root_open
import rootUtils as ut
import shipunit as u


@click.command()
@click.argument('inputfile')
@click.argument('geofile')
@click.option('-o', '--output', default='muConcrete.root')
@click.option('-v', '--volume', default='rockD')
def makeMuonInelasticTuple(inputfile, output, geofile, volume):
    h = {}
    for m in ['mu', 'V0']:
        ut.bookHist(h, 'conc_hitz' + m, 'concrete hit z ' + m, 100, -100.,
                    100.)
        ut.bookHist(h, 'conc_hitzP' + m, 'concrete hit z vs P' + m, 100, -100.,
                    100., 100, 0., 25.)
        ut.bookHist(h, 'conc_hity' + m, 'concrete hit y ' + m, 100, -15., 15.)
        ut.bookHist(h, 'conc_p' + m, 'concrete hit p ' + m, 1000, 0., 400.)
        ut.bookHist(h, 'conc_pt' + m, 'concrete hit pt ' + m, 100, 0., 20.)
        ut.bookHist(h, 'conc_hitzy' + m, 'concrete hit zy ' + m, 100, -100.,
                    100., 100, -15., 15.)
    ntuple = r.TNtuple('muons', 'muon flux concrete', 'id:px:py:pz:x:y:z:w')
    f = r.TFile.Open(inputfile)
    tree = f.cbmsim
    with root_open(geofile) as fgeo:
        sGeo = fgeo.FAIRGeom
    for event in tree:
        weight = (event.MCTrack[1].GetWeight()
                  if event.MCTrack.GetEntries() > 1
                  else event.MCTrack[0].GetWeight())
        for hit in event.vetoPoint:
            detID = hit.GetDetectorID()
            if detID>10000:
                continue
            node=sGeo.FindNode(hit.GetX(),hit.GetY(),hit.GetZ())
            if not volume in node.GetName():
                continue
            pid = hit.PdgCode()
            if abs(pid) != 13:
                continue
            m = 'mu'
            P = r.TMath.Sqrt(hit.GetPx()**2 + hit.GetPy()**2 + hit.GetPz()**2)
            if P > 3 / u.GeV:
                m = 'V0'
                ntuple.Fill(
                    float(pid),
                    float(hit.GetPx() / u.GeV),
                    float(hit.GetPy() / u.GeV),
                    float(hit.GetPz() / u.GeV),
                    float(hit.GetX() / u.m),
                    float(hit.GetY() / u.m),
                    float(hit.GetZ() / u.m), float(weight))
            h['conc_hitz' + m].Fill(hit.GetZ() / u.m, weight)
            h['conc_hity' + m].Fill(hit.GetY() / u.m, weight)
            h['conc_p' + m].Fill(P / u.GeV, weight)
            h['conc_hitzP' + m].Fill(hit.GetZ() / u.m, P / u.GeV, weight)
            Pt = np.hypot(hit.GetPx(), hit.GetPy())
            h['conc_pt' + m].Fill(Pt / u.GeV, weight)
            h['conc_hitzy' + m].Fill(hit.GetZ() / u.m,
                                     hit.GetY() / u.m, weight)
    ut.bookCanvas(
        h,
        key='ResultsV0',
        title='muons hitting concrete, p>3GeV',
        nx=1000,
        ny=600,
        cx=2,
        cy=2)
    ut.bookCanvas(
        h,
        key='Resultsmu',
        title='muons hitting concrete',
        nx=1000,
        ny=600,
        cx=2,
        cy=2)
    ut.bookCanvas(
        h,
        key='Results',
        title='hitting concrete',
        nx=1000,
        ny=600,
        cx=2,
        cy=2)
    for m in ['mu', 'V0']:
        tc = h['Results' + m].cd(1)
        h['conc_hity' + m].Draw()
        tc = h['Results' + m].cd(2)
        h['conc_hitz' + m].Draw()
        tc = h['Results' + m].cd(3)
        tc.SetLogy(1)
        h['conc_pt' + m].Draw()
        tc = h['Results' + m].cd(4)
        tc.SetLogy(1)
        h['conc_p' + m].Draw()
    ut.writeHists(h, output)
    with root_open(output, 'update'):
        ntuple.Write()

if __name__ == '__main__':
    makeMuonInelasticTuple()
