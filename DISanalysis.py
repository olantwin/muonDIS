import ROOT as r
import math
import rootUtils as ut
import argparse
import shipVeto
from ShipGeoConfig import ConfigRegistry
import shipunit as u
from numpy import ndarray
import numpy as np
r.PyConfig.IgnoreCommandLineOptions = True
import gc

def analysis():


	def prob2int(cross,weight):
		#multiple the cross section in mbarn
		prob2int=(cross*1e-27*6.022e+23*weight)
		return prob2int



	#DEFINITION OF ALL CUTS USED IN THE ANALYSIS


	def isInFiducial(Z):
  		if Z > trackST1 : return False
   		if Z < startDecayVol: return False
   		return True 

	
	def ImpactParameter(point,tPos,tMom):
  		t = 0
  		if hasattr(tMom,'P'): 
			P = tMom.P()

		else:                 
			P = tMom.Mag()

		
  		for i in range(3):   
			t += tMom(i)/P*(point(i)-tPos(i))
  		dist = 0
  		for i in range(3):  
			dist += (point(i)-tPos(i)-t*tMom(i)/P)**2
  		dist = r.TMath.Sqrt(dist)
  		return dist



	parser= argparse.ArgumentParser(description='Script to makeAnalysis')
    	parser.add_argument(
		'-g',
        	'--geofile',
		 help='''Geometry file to use. ''')
	
    	parser.add_argument(
		'-f',
        	'--inputFile',
		 help='''Input file to use. ''')
	
	
    	parser.add_argument(
        	'-o',
        	'--outputfile',
        	default='muonDISstudy.root')
    	args = parser.parse_args()

    	g = r.TFile.Open(args.geofile, 'read')
    	sGeo = g.FAIRGeom
	f = r.TFile.Open(args.inputFile, 'read')
    	o = r.TFile.Open(args.outputfile, 'recreate')

	#define the histograms
	pdg=r.TParticlePDG()
   	h={}	
	ut.bookHist(h,'hprob2int',';Probability to interact;Nentries',1000,0.,1.)
	ut.bookHist(h,'htotalWeight',';Total Weight;Nentries',1000,0.,1.)
	
	ut.bookHist(h,'hmass_rec','The invarian mass of the HNL candidate ;M[GeV]; Nentries',100,0.,10)
	ut.bookHist(h,'hdoca','Distance of closest aproach  ;DOCA[cm]; Nentries',200,0.,10000)
	
	ut.bookHist(h,'hip','The Impact Parameter  ;IP[cm]; Nentries',500,0.,4000)

	ut.bookHist(h, 'hipFidCut5cm', 'The Impact Parameter  ;IP[cm]; Nentries',500,0.,40000)

	ut.bookHist(h,'hipDocaCut','The Impact Parameter  ;IP[cm]; Nentries',500,0.,40000) 
	ut.bookHist(h,'hdocaIP250Cut','Distance of closest aproach  ;DOCA[cm]; Nentries',200,0.,10000)
	
	ut.bookHist(h,'hdocaIP10Cut','Distance of closest aproach  ;DOCA[cm]; Nentries',200,0.,10000)
	
	ut.bookHist(h,'hdocaIP30Cut','Distance of closest aproach  ;DOCA[cm]; Nentries',200,0.,10000)
	ut.bookHist(h,'hmass_ip',";mass[GeV/c];IP[cm]",100,0,10,500,0.,4000)
	ut.bookHist(h,'hdocaSBTcut', 'Distance of closest aproach  ;DOCA[cm]; Nentries',200,0.,10000)
	ut.bookHist(h, 'hIP5cm', 'IP of HNL candidate ;IP[cm];Entries ',200,0.,10000)
	ut.bookHist(h,'hdoca2cut','Distance of closest aproach  ;DOCA[cm]; Nentries',200,0.,1)
	ut.bookHist(h,'hdoca3cut','Distance of closest aproach  ;DOCA[cm]; Nentries',200,0.,1)
	
	ut.bookHist(h,'hdocaIP250', 'The doca of the HNL event;DOCA[cm];Nentries',200,0.,10000)
	ut.bookHist(h,'hHNLafterVeto','', 1,0.,1)
	ut.bookHist(h, 'hIP5cmFully', 'IP of HNL candidate ;IP[cm];Entries ',200,0.,10000)
	ut.bookHist(h,'hdoca2cutFully','Distance of closest aproach  ;DOCA[cm]; Nentries',200,0.,1)
	ut.bookHist(h,'hdoca3cutIP10','Distance of closest aproach  ;DOCA[cm]; Nentries',200,0.,1)
	ut.bookHist(h,'hHNLafterVetoIP10','', 1,0.,1)
	ut.bookHist(h, 'PidInIP10', 'The info of the reconstructed track in the spectrometer using the pid', 10,-5,5.)
	ut.bookHist(h,'mom1mom2hnlPass10IPcut','MotherIds of HNL candidate', 10000,-5000,5000,10000,-5000,5000)
	ut.bookHist(h, 'Mc1Mc2hnlPass10IPcut', 'Pdg of the Monte  Carlo particles "coming " from HNL decay',10000,-5000,5000)
	ut.bookHist(h, 'hIP7cm', 'IP of HNL candidate ;IP[cm];Entries ',200,0.,10000)
	ut.bookHist(h,'hdoca2cut7cm','Distance of closest aproach  ;DOCA[cm]; Nentries',200,0.,1)
	ut.bookHist(h,'hdoca3cutIP2507cm','Distance of closest aproach  ;DOCA[cm]; Nentries',200,0.,1)
	ut.bookHist(h, 'PidInIP2507cm', 'The info of the reconstructed track in the spectrometer using the pid', 10,-5,5.)
	ut.bookHist(h,'mom1mom2hnlPass250IPcut7cm','MotherIds of HNL candidate', 10000,-5000,5000,10000,-5000,5000)
	ut.bookHist(h, 'Mc1Mc2hnlPass250IPcut7cm', 'Pdg of the Monte  Carlo particles "coming " from HNL decay',10000,-5000,5000,10000,-5000,5000)
	ut.bookHist(h,'hHNLafterVetoIP2507cm','', 1,0.,1)
	

	

	


	
	


	ut.bookHist(h,'hNumTrack','Number of reconstructed tracks in the Spectrometer',11 , 0.5,10.5)

	
	ut.bookHist(h,'docaHNLcandidateComingFromDiffM','Distance of closest aproach for reconstructed HNL coming from different Mothers  ;DOCA[cm]; Nentries',200,0.,10000)
	ut.bookHist(h,'IPHNLcandidateComingFromDiffM', 'IP of Reconstructed HNL candidate coming from different Mothers;IP[cm];Entries ',200,0.,10000)
		
	ut.bookHist(h,'docaHNLcandidateComingFromSameM','Distance of closest aproach for reconstructed HNL coming from the same mother  ;DOCA[cm]; Nentries',200,0.,10000)
	ut.bookHist(h,'IPHNLcandidateComingFromSameM', 'IP of Reconstructed HNL candidate coming from the same mother;IP[cm];Entries ',200,0.,10000)
		
	ut.bookHist(h,'PDGMother', 'The Pdg code of the mother Particle for the reconstructed HNL', 10000,-5000,5000)
	ut.bookHist(h,'xyDISVertex', ' The vertex position of the DIS events',300,-15,15,300,-15,15)
        ut.bookHist(h,'xzDISVertex', ' The vertex position of the DIS events',600,-30,30,300,-15,15)
        ut.bookHist(h,'yzDISVertex', ' The vertex position of the DIS events',600,-30,30,300,-15,15)
        ut.bookHist(h,'rhoL', 'The rhoL of the DIS events', 10000, 0. , 10000)
	ut.bookHist(h,'weightOFMuon', 'The weight of the intial muon', 900,0.5,900.5)
	ut.bookHist(h,'hdisToWallMCvertex', ' Distance beetwen the MC DIS Vertex and the Wall ',100,0.,5)
	ut.bookHist(h,'hNumHNLParticle','Number of Reconstructed HNL per event',10,0.5,9.)
	ut.bookHist(h,'mom1mom2DiffMother','MotherIds of HNL candidate', 10000,-5000,5000,10000,-5000,5000)
	ut.bookHist(h, 'Mc1Mc2DiffMother', 'Pdg of the Monte  Carlo particles "coming " from HNL decay',10000,-5000,5000,10000,-5000,5000)
	ut.bookHist(h,'distToWallRecHNL', ' Distance beetwen the HNL Vertex and the wall ',200,0.,200)
	ut.bookHist(h, 'PidIn', 'The info of the reconstructed track in the spectrometer using the pid', 10,-5,5.)
	ut.bookHist(h,'mom1mom2hnlPass250IPcut','MotherIds of HNL candidate', 10000,-5000,5000,10000,-5000,5000)
	ut.bookHist(h, 'Mc1Mc2hnlPass250IPcut', 'Pdg of the Monte  Carlo particles "coming " from HNL decay',10000,-5000,5000)
	#ut.bookHist(h, 'hdeltaXYZ130', 'The end Vertex of Klong particle',100,-50,50,12,0,12) 
	ut.bookHist(h, 'hdeltaXYZ310', 'The end Vertex of Kshort particle',100,-50,50,1200,0,12) 
	ut.bookHist(h, 'hdeltaXYZ3122', 'The end Vertex of Kshort particle',100,-50,50,1200,0,12) 
	ut.bookHist(h, 'hdeltaXYZ130', 'The end Vertex of Klong',100,-50,50,1200,0,12) 
	ut.bookHist(h, 'hPidCut', 'Events passing the cut ',10,-5,5) 


	#define some variable need it to estimate the IP , dis2Target

	ShipGeo = ConfigRegistry.loadpy("$FAIRSHIP/geometry/geometry_config.py",Yheight = 10, tankDesign = 6 , muShieldDesign = 9, nud=3,caloDesign=3,strawDesign=10)
	startDecayVol=ShipGeo.vetoStation.z+20.*u.cm
	trackST1=ShipGeo.TrackStation1.z-20*u.cm
	
	print "The start Position of the Decay Volume=", startDecayVol
	print "The end Position of the Decay Volume =", trackST1



	ch = r.TChain('cbmsim')
	ch.Add(args.inputFile)
	nev = ch.GetEntries()
	o.cd()
	print "The number of events is=", nev

	veto=shipVeto.Task(ch)

	numbermuon=0
	ev=0
	for event in ch:
		ev=ev+1
		evDic3122=[]	
		evDic130=[]
		evDic310=[]
		#the initial muon having the weight to have full statistics of the full spill
		muWeight=event.MCTrack[1].GetWeight()
		#print "The weight is=",muWeight
		#the cross section for DIS(Pythia[mbarn] 
		cross=event.MCTrack[0].GetWeight()
		#print "The cross section is =", cross
		# the rhoL of the initial muon 
    		weight=event.MCTrack[3].GetWeight()
		h['weightOFMuon'].Fill(muWeight,0.0001)	
		h['rhoL'].Fill(weight,0.0001)
		#print "The weight is=", weight
    		P=event.MCTrack[0].GetP()
		Z=event.MCTrack[0].GetStartZ()
		prob=prob2int(cross,weight)
		
		
		totalWeight=prob*muWeight
		#print "The totalWeight", totalWeight
		#make V0 decay 
		#print " The number of ev=", ev
		for track in event.MCTrack:
			if event.MCTrack.index(track)>0:
				deltaXY=math.sqrt(track.GetStartX()**2+track.GetStartY()**2)
				deltaZ=track.GetStartZ()-startDecayVol
				pdgMother=event.MCTrack[track.GetMotherId()].GetPdgCode()
					#lambda
				if pdgMother== 3122:
					if ev not in evDic3122:
						evDic3122.append(ev)
						h['hdeltaXYZ3122'].Fill(deltaZ/100,deltaXY/100,totalWeight)
				#kshort
				if pdgMother==310:
					if ev not in evDic310:
						evDic310.append(ev)

						h['hdeltaXYZ310'].Fill(deltaZ/100,deltaXY/100,totalWeight)
									
				#klong
				if pdgMother==130:
					if ev not in evDic130:
						evDic130.append(ev)
						h['hdeltaXYZ130'].Fill(deltaZ/100,deltaXY/100,totalWeight)
					





    		px=event.MCTrack[0].GetPx()
    		py=event.MCTrack[0].GetPy()
    		pz=event.MCTrack[0].GetPz()
		h['hprob2int'].Fill(prob,0.0001)
		#h['htotalWeight'].Fill(totalWeight,totalWeight)
		numbermuon+=muWeight
		#make plots for the x,y,z position where you put the DIS events
		h['xyDISVertex'].Fill(event.MCTrack[0].GetStartX()/100,event.MCTrack[0].GetStartY()/100,totalWeight)	
		h['xzDISVertex'].Fill(event.MCTrack[0].GetStartZ()/100,event.MCTrack[0].GetStartX()/100,totalWeight)	
		h['yzDISVertex'].Fill(event.MCTrack[0].GetStartZ()/100,event.MCTrack[0].GetStartY()/100,totalWeight)
		VertexP=r.TVector3(event.MCTrack[0].GetStartX(),event.MCTrack[0].GetStartY(),event.MCTrack[0].GetStartZ())
		disToWallMCvertex=veto.fiducialCheck(VertexP)	
		h['hdisToWallMCvertex'].Fill(disToWallMCvertex)
		#print sGeo.FindNode(event.MCTrack[0].GetStartX(),event.MCTrack[0].GetStartY(),event.MCTrack[0].GetStartZ())
		numTrack=len(event.goodTracks)
		h['hNumTrack'].Fill(numTrack)
		numHNLParticle=len(event.Particles)

		h['hNumHNLParticle'].Fill(numHNLParticle)
    		
		if numTrack==2:
			vetoSBT,nHitSBT,wSBT = veto.SBT_decision() 	
			vetoRPC,nHitRPC,wRPC = veto.RPC_decision() 	

			for candidate in event.Particles:
				#define 3,4 Momentum Vector,vtarget
				vtx = r.TVector3()
				momentumHNL=r.TLorentzVector()
				vtarget=r.TVector3(0,0,ShipGeo.target.z0)
				indexCandidate=event.Particles.index(candidate)
				candidate.GetVertex(vtx)
				candidate.GetMomentum(momentumHNL)
				mass_rec=momentumHNL.Mag2()
				doca=candidate.GetDoca()
				ip=ImpactParameter(vtarget,vtx,momentumHNL)
				distToWall=veto.fiducialCheckSignal(indexCandidate)
				#h['distToWallRecHNL'].Fill(distToWall)
				d1 =int( candidate.GetDaughter1())
				d2=  int(candidate.GetDaughter2())

				# the fitTrack2MC leave is an array of the same length as FitTracks.
				# it contains the index of the corresponding MCTrack.
				#print event.fitTrack2MC[0]
				d1_mc= event.fitTrack2MC[d1]
				d2_mc= event.fitTrack2MC[d2]
				pdgMC1=event.MCTrack[d1_mc].GetPdgCode()
				pdgMC2=event.MCTrack[d2_mc].GetPdgCode()
				mum1 = event.MCTrack[d1_mc].GetMotherId()
				mum2 = event.MCTrack[d2_mc].GetMotherId()
				pdgMom1=event.MCTrack[mum1].GetPdgCode()
				pdgMom2=event.MCTrack[mum2].GetPdgCode()	

				






					
				if not event.MCTrack[mum1].GetPdgCode() == event.MCTrack[mum2].GetPdgCode():
					h['docaHNLcandidateComingFromDiffM'].Fill(doca)
					h['IPHNLcandidateComingFromDiffM'].Fill(ip)
					h['mom1mom2DiffMother'].Fill(pdgMom1,pdgMom2)
					h['Mc1Mc2DiffMother'].Fill(pdgMC1,pdgMC2)
					
				else:
					h['PDGMother'].Fill(event.MCTrack[mum1].GetPdgCode())
					h['docaHNLcandidateComingFromSameM'].Fill(doca)
					h['IPHNLcandidateComingFromSameM'].Fill(ip)
			
				








				h['hmass_rec'].Fill(mass_rec,totalWeight)
				h['hdoca'].Fill(doca,totalWeight)		
				h['hip'].Fill(ip,totalWeight)
				#Use veto systems 

				

				
				if (distToWall>5*u.cm and distToWall!=0 and isInFiducial(vtx.Z())==True):
					h['hipFidCut5cm'].Fill(ip,totalWeight)
						

						
				
				if doca<1:
					h['hipDocaCut'].Fill(ip,totalWeight)
					
						
				
				
				
				
				if ip<10:
					h['hdocaIP10Cut'].Fill(doca,totalWeight)

					





				if ip<250:
					h['hdocaIP250Cut'].Fill(doca,totalWeight)

					

				if ip<30:
					h['hdocaIP30Cut'].Fill(doca,totalWeight)

					



				
				if vetoSBT == False and vetoRPC == False :
					h['hmass_ip'].Fill(ip,totalWeight)
				
				if vetoSBT == False:
					h['hdocaSBTcut'].Fill(doca,totalWeight)

				# look for partially Reconstructed 

				if distToWall>5*u.cm and distToWall!=0 and isInFiducial(vtx.Z())==True:
					h['hIP5cm'].Fill(ip,totalWeight)
				
				
					if doca<1:
						print "The doca is =", doca
						h['hdoca2cut'].Fill(doca,totalWeight)
						
						if ip<250:

							
							h['hdoca3cut'].Fill(doca,totalWeight)
							print "THe mothers are :", pdgMom1, pdgMom2,mum1,mum2
							print "THe tracks are :", pdgMC1, pdgMC2,d1_mc,d2_mc
							h['mom1mom2hnlPass250IPcut'].Fill(pdgMom1,pdgMom2)
							h['Mc1Mc2hnlPass250IPcut'].Fill(pdgMC1,pdgMC2)
							pidTracks=event.Pid.GetEntriesFast()
							if event.Pid[0].TrackPID() > 0 and event.Pid[1].TrackPID() > 0:
								h['hPidCut'].Fill(1, totalWeight)
							for p in event.Pid:
								PidS=p.TrackPID()
								h['PidIn'].Fill(PidS)



							if vetoSBT == False   and  vetoSVT == False and vetoRPC == False:
								h['hHNLafterVeto'].Fill(1, totalWeight)

		
				if distToWall>5*u.cm and distToWall!=0 and isInFiducial(vtx.Z())==True:
					h['hIP5cmFully'].Fill(ip,totalWeight)
				
				
					if doca<1:
						h['hdoca2cutFully'].Fill(doca,totalWeight)

							#print "Yes i am passing the event"
						if ip<10:

							
							h['hdoca3cutIP10'].Fill(doca,totalWeight)
							h['mom1mom2hnlPass10IPcut'].Fill(pdgMom1,pdgMom1)
							h['Mc1Mc2hnlPass10IPcut'].Fill(pdgMC1,pdgMC2)
							for p in event.Pid:
								PidF=p.TrackPID()
								h['PidInIP10'].Fill(PidF)




							if vetoSBT == False   and  vetoSVT == False and vetoRPC == False:
								h['hHNLafterVetoIP10'].Fill(1, totalWeight)
				

				
				if distToWall>7*u.cm and distToWall!=0 and isInFiducial(vtx.Z())==True:
					h['hIP7cm'].Fill(ip,totalWeight)
				
				
					if doca<1:
						h['hdoca2cut7cm'].Fill(doca,totalWeight) 	

							#print "Yes i am passing the event"
						if ip<250:

							
							h['hdoca3cutIP2507cm'].Fill(doca,totalWeight)

							h['mom1mom2hnlPass250IPcut7cm'].Fill(pdgMom1,pdgMom2)
							h['Mc1Mc2hnlPass250IPcut7cm'].Fill(pdgMC1,pdgMC2)
							for p in event.Pid:
								PidF7cm=p.TrackPID()
								h['PidInIP2507cm'].Fill(PidF7cm)




							if vetoSBT == False   and  vetoSVT == False and vetoRPC == False:
								h['hHNLafterVetoIP2507cm'].Fill(1, totalWeight)
			






	
		
	print "The total number of muons =", numbermuon
	print 'Event loop done'
	for key in h:
		h[key].Write()
	o.Close()


if __name__ == '__main__':
    analysis()
	
