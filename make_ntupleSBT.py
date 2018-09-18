import ROOT as r
import os,sys,getopt
import rootUtils as ut
import argparse
import time
import math
from ShipGeoConfig import ConfigRegistry
import shipunit as u
import numpy as np
r.PyConfig.IgnoreCommandLineOptions = True
parser= argparse.ArgumentParser(description='Script to collect muons hitting the SBT')
hnumSegPermmuon=r.TH1I('hnumSegPermmuon', 'Numbers of fired segments per muon',200, 0., 200)
hPmuon=r.TH1F('hPmuon','The momentum of the muons hitting the SBT', 400, 0.,400)


parser.add_argument(
	'-f',
	'--inputFile',
	 help='''Input file to use. ''')


parser.add_argument(
	'-o',
	'--outputfile',
	default='muonsNewProduction.root')
args = parser.parse_args()
ev=0
h={}

f = r.TFile.Open(args.inputFile, 'read')
o = r.TFile.Open(args.outputfile, 'recreate')
tree=f.cbmsim
h['ntuple'] = r.TNtuple('muonsSBT', 'muon flux InnerWall', 'id:px:py:pz:x:y:z:w')
dic=[]

for event in tree:
	ev=ev+1

	numHitsPermuon=0
     	for hit in event.vetoPoint:
		detID = hit.GetDetectorID()
                pid = hit.PdgCode()
		trackID=hit.GetTrackID()
		if detID>1000 and  detID<999999 and abs(pid)==13:
 	       		if ev not in  dic:
     	       			dic.append(ev)
                		numHitsPermuon+=1
                		P = r.TMath.Sqrt(hit.GetPx()**2 + hit.GetPy()**2 + hit.GetPz()**2)
				weight=tree.MCTrack[trackID].GetWeight()
				hPmuon.Fill(P,weight)

                		if P > 3 / u.GeV:
     	       				h['ntuple'].Fill(
                			float(pid),
     	       				float(hit.GetPx() / u.GeV),
     	       				float(hit.GetPy() / u.GeV),
 	       				float(hit.GetPz() / u.GeV),
     	       				float(hit.GetX() / u.m),
					float(hit.GetY() / u.m),
					float(hit.GetZ() / u.m), float(weight))
			else:
				numHitsPermuon+=1
	if numHitsPermuon!=0:hnumSegPermmuon.Fill(numHitsPermuon)
	
o.cd()
h['ntuple'].Write()
hnumSegPermmuon.Write()
hPmuon.Write()






