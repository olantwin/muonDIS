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
parser= argparse.ArgumentParser(description='Script to collect muons hitting the Tr1')
hnumSegPermmuon=r.TH1I('hnumSegPermmuon', 'Numbers of fired segments per muon',200, 0., 200)
hPmuon=r.TH1F('hPmuon','The momentum of the muons hitting the SBT from the new Muon Background production 2018, Energy cut 3GeV;P[GeV];Entries', 400, 0.,400)
hDetID=r.TH1I('hDetID', 'The detID of all hits inside the vetoPont',1000,0.,1000)
hThetaPhi=r.TH2D('hThetaPhi', "The Z position of the muon Hit in the SBT  vs Phi ", 100, -3000, +3000, 100, -r.TMath.Pi(), r.TMath.Pi())
hDetIDS=r.TH1I('hDetIDS', "The detector ID  - muons hitting the straws ", 5,0.,5)


parser.add_argument(
	'-f',
	'--inputFile',
	 help='''Input file to use. ''')
parser.add_argument(
	'-o',
	'--outputfile',
	default='muonsNewProductionTr1.root')
args = parser.parse_args()
ev=0
h={}

f = r.TFile.Open(args.inputFile, 'read')
o = r.TFile.Open(args.outputfile, 'recreate')
tree=f.cbmsim
h['ntuple'] = r.TNtuple('muonsTr1', 'muon flux Tracking station 1', 'id:px:py:pz:x:y:z:w')
dic=[]


for event in tree:
	ev=ev+1
	trackDic=[]
	strawDic=[]
	numHitsPermuon=0
	#loop over all hits in the SBT and save the tracks ID of all muons  in list strawDic
	for strawHit in event.strawtubesPoint:
		P = r.TMath.Sqrt(strawHit.GetPx()**2 + strawHit.GetPy()**2 + strawHit.GetPz()**2) 

                if P >  3:
			detIDmuonS=strawHit.GetDetectorID()/10000000
			if abs(strawHit.PdgCode())==13 and detIDmuonS==1:
				if not strawHit.GetTrackID() in strawDic:
					strawDic.append(strawHit.GetTrackID())
					hDetIDS.Fill(detIDmuonS)

	#loop over all hits in the Tr1  and save the tracks ID of all muons  in list trackDic

	for hit in event.vetoPoint:
		detID = hit.GetDetectorID()
		pid = hit.PdgCode()
		trackID=hit.GetTrackID()
		if detID>1000 and  detID<999999 and abs(pid)==13:
			if trackID not in trackDic:
				trackDic.append(trackID)
	counMuonsOne=[]
	'''Loop over the trackID of the muons in the  lists to check how many muons hit the Tr1, but doesn't hit the SBT and save them in ntuple.
	These muons are passing throught the whole Vessel and  could produced background  for Fully reconstructd HNL final states'''
	for m in strawDic:
	 	if m not in trackDic:
			for Hit in event.strawtubesPoint:
                        	detID = Hit.GetDetectorID()
                        	pid = Hit.PdgCode()
                        	trackID=Hit.GetTrackID()
				if m==trackID:
					if m not in counMuonsOne:
						counMuonsOne.append(m)
						
					
						P = r.TMath.Sqrt(Hit.GetPx()**2 + Hit.GetPy()**2 + Hit.GetPz()**2)
						weight=tree.MCTrack[m].GetWeight()		
						hPmuon.Fill(P,weight)
						h['ntuple'].Fill(
						float(pid),
						float(Hit.GetPx() / u.GeV),
						float(Hit.GetPy() / u.GeV),
						float(Hit.GetPz() / u.GeV),
						float(Hit.GetX() / u.m),
						float(Hit.GetY() / u.m),
						float(Hit.GetZ() / u.m), float(weight))
				#else:
					#numHitsPermuon+=1
	#	if numHitsPermuon!=0:hnumSegPermmuon.Fill(numHitsPermuon)
		
o.cd()
h['ntuple'].Write()
#hnumSegPermmuon.Write()
hPmuon.Write()
#hDetID.Write()
#hDetIDS.Write()
