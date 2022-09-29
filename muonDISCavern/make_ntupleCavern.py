import ROOT as r
import os,sys,getopt
import rootUtils as ut
import argparse
import time
import math
from ShipGeoConfig import ConfigRegistry
import shipunit as u
import numpy as np
import pylab
r.PyConfig.IgnoreCommandLineOptions = True
parser= argparse.ArgumentParser(description='Script to makeAnalysis')
hnumSegPermmuon=r.TH1I('hnumSegPermmuon', 'Numbers of fired segments per muon',200, 0., 200)
hPInitialM=r.TH1F('hPInitialM','The momentum of the Initial  muons from the new Muon Background production 2018;P[GeV];Entries', 400, 0.,400)
hPCavern=r.TH1F('hPCavern','The momentum of the Initial  muons from the new Muon Background production 2018;P[GeV];Entries', 400, 0.,400)

#hPmuon=r.TH1F('hPmuon','The momentum of the Initial  muons hitting the SBT with 3GeV from the new Muon Background production 2018;P[GeV];Entries', 400, 0.,400)

xy=r.TH2D('xy',";Y[m];X[m]",30,-15,15,30,-15,15)
xz=r.TH2D('xz',";Z[m];X[m]",180,-60,120,30,-15,15)
xyz=r.TH3D('xyz',"XYZ position of muons with 3GeV momentum cut in the cavern", 10,-15,15,10,-15,15,10,-60,120)







#hTime=r.TH1D('hTime', "the time difference beetwen the time when muon hit the Muon Detector and the cavern",2000,-1000., 1000)


parser.add_argument(
	'-f',
	'--inputFile',
	required=True,
	 help='''Input file to use. ''')

parser.add_argument(
	'-g',
	'--geoFile',
	required=True,
	 help='''GeoFile file to use. ''')




pdg=r.TDatabasePDG.Instance()



parser.add_argument(
	'-o',
	'--outputfile',
	default='muonsNewProduction.root')
args = parser.parse_args()
ev=0
h={}


o = r.TFile.Open(args.outputfile, 'recreate')
h['ntuple'] = r.TNtuple('muonsSBT', 'muon flux cavern', 'id:px:py:pz:x:y:z:w')
f = r.TFile.Open(args.inputFile, 'read')
g=r.TFile.Open(args.geoFile,'read')
sGeo=g.FAIRGeom
tree=f.cbmsim

dic=[]
muonCavern=[]
lis=[]

#print "The events aree =", tree.GetEntries()

for event in tree:
	
	ev=ev+1
	#print "The event number is =", ev
	numHitsPermuon=0
	for track in event.MCTrack:
	
		if abs(track.GetPdgCode())== 13:
			hPInitialM.Fill(track.GetP(),track.GetWeight())





	for hit in event.vetoPoint:
		pid = hit.PdgCode()
		trackID=hit.GetTrackID()
		name= (sGeo.FindNode(hit.GetX(),hit.GetY(),hit.GetZ())).GetName()
		if name in 'Cavern_1' and abs(pid)==13 :
			P = r.TMath.Sqrt(hit.GetPx()**2 + hit.GetPy()**2 + hit.GetPz()**2)
			#print "Track ID is=", trackID, "The particle is=",tree.MCTrack[trackID].GetPdgCode(), "The weight is=", tree.MCTrack[trackID].GetWeight()
			hPCavern.Fill(P,tree.MCTrack[trackID].GetWeight())
			a=hit.LastPoint()
			X=hit.GetX()
			Y=hit.GetY()
			Z=hit.GetZ()
			hitStartX=(2*X-a.X()) / u.m	
			hitStartY=(2*Y-a.Y()) / u.m	
			hitStartZ=(2*Z-a.Z()) / u.m
			xz.Fill(hitStartZ,hitStartX)
			xy.Fill(hitStartY,hitStartX)
			xyz.Fill(hitStartX,hitStartY,hitStartZ)
			

			if P > 3:
				weight=tree.MCTrack[trackID].GetWeight()

				#print "The satrt dosition in the cavern =", hitStartX,hitStartY, hitStartZ,trackID
				if hitStartZ < 35:

					h['ntuple'].Fill(
					float(pid),
					float(hit.GetPx() ),
					float(hit.GetPy() ),
					float(hit.GetPz()),
					float(hitStartX ),
					float(hitStartY ),
					float(hitStartZ ), float(weight))
			



o.cd()
h['ntuple'].Write()
hPInitialM.Write()
hPCavern.Write()
#hPmuon.Write()
#hTime.Write()
xz.Write()
xy.Write()
xyz.Write()
