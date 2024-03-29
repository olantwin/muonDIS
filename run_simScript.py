#!/usr/bin/env python 
import ROOT,os,sys,getopt,time
import shipunit as u
import shipRoot_conf
import rootUtils as ut
from ShipGeoConfig import ConfigRegistry

debug = 0  # 1 print weights and field
           # 2 make overlap check
# Default HNL parameters
theMass = 1.0*u.GeV
theCouplings = [0.447e-9, 7.15e-9, 1.88e-9] # ctau=53.3km  TP default for HNL

# Default dark photon parameters
theDPmass = 0.2*u.GeV
theDPepsilon = 0.00000008

mcEngine     = "TGeant4"
simEngine    = "muonDIS"  # "Genie" # Ntuple
nEvents      = 1
firstEvent   = 0
inclusive    = "c"    # True = all processes if "c" only ccbar -> HNL, if "b" only bbar -> HNL, and for darkphotons: if meson = production through meson decays, pbrem = proton bremstrahlung, qcd = ffbar -> DP.
deepCopy     = False  # False = copy only stable particles to stack, except for HNL events
MCTracksWithHitsOnly   = False  # copy particles which produced a hit and their history
MCTracksWithEnergyCutOnly = True # copy particles above a certain kin energy cut
MCTracksWithHitsOrEnergyCut = False # or of above, factor 2 file size increase compared to MCTracksWithEnergyCutOnly

charmonly    = False  # option to be set with -A to enable only charm decays, charm x-sec measurement  
HNL          = True
DarkPhoton   = False
RPVSUSY      = False
RPVSUSYbench = 2

eventDisplay = False
inputFile    = "/eos/experiment/ship/data/Charm/Cascade-parp16-MSTP82-1-MSEL4-978Bpot.root"

defaultInputFile = True
outputDir    = "."
sameSeed     = False # can be set to an integer for the muonBackground simulation with specific seed for each muon 
theSeed      = int(10000 * time.time() % 10000000)

globalDesigns = {'2016':{'dy':10.,'dv':5,'ds':7,'nud':1,'caloDesign':0,'strawDesign':4},\
                 '2018':{'dy':10.,'dv':6,'ds':9,'nud':3,'caloDesign':3,'strawDesign':10}}
default = '2018'

dy           = globalDesigns[default]['dy'] # max height of vacuum tank
dv           = globalDesigns[default]['dv'] # 4=TP elliptical tank design, 5 = optimized conical rectangular design, 6=5 without segment-1
ds           = globalDesigns[default]['ds'] # 5=TP muon shield, 6=magnetized hadron, 7=short magnet design, 9=optimised with T4 as constraint, 8=requires config file
nud          = globalDesigns[default]['nud'] # 0=TP, 1=new magnet option for short muon shield, 2= no magnet surrounding neutrino detector
caloDesign   = globalDesigns[default]['caloDesign'] # 0=ECAL/HCAL TP  1=ECAL/HCAL TP + preshower 2=splitCal  3=ECAL/ passive HCAL 
strawDesign  = globalDesigns[default]['strawDesign'] # simplistic tracker design,  4=sophisticated straw tube design, horizontal wires (default), 10=2cm straw diameter for 2018 layout

charm        = 0 # !=0 create charm detector instead of SHiP
geofile = None

inactivateMuonProcesses = False   # provisionally for making studies of various muon background sources
checking4overlaps = False
if debug>1 : checking4overlaps = True
phiRandom   = False  # only relevant for muon background generator
followMuon  = False  # make muonshield active to follow muons
fastMuon    = False  # only transport muons for a fast muon only background estimate
nuRadiography = False # misuse GenieGenerator for neutrino radiography and geometry timing test
Opt_high = None # switch for cosmic generator
try:
        opts, args = getopt.getopt(sys.argv[1:], "D:FHPu:n:i:f:c:hqv:s:l:A:Y:i:m:co:t:g",[\
                                   "PG","Pythia6","Pythia8","Genie","MuDIS","Ntuple","Nuage","MuonBack","FollowMuon","FastMuon",\
                                   "Cosmics=","nEvents=", "display", "seed=", "firstEvent=", "phiRandom", "mass=", "couplings=", "coupling=", "epsilon=",\
                                   "output=","tankDesign=","muShieldDesign=","NuRadio","test",\
                                   "DarkPhoton","RpvSusy","SusyBench=","sameSeed=","charm=","nuTauTargetDesign=","caloDesign=","strawDesign="])

except getopt.GetoptError:
        # print help information and exit:
        print ' enter --Pythia8 to generate events with Pythia8 (-A b: signal from b, -A c: signal from c (default)  or -A inclusive)'
        print ' or    --Genie for reading and processing neutrino interactions '
        print ' or    --Pythia6 for muon nucleon scattering'  
        print ' or    --PG for particle gun'  
        print '       --MuonBack to generate events from muon background file, --Cosmics=0 for cosmic generator data'  
        print '       --RpvSusy to generate events based on RPV neutralino (default HNL)'
        print '       --DarkPhoton to generate events with dark photons (default HNL)'
        print ' for darkphoton generation, use -A meson or -A pbrem or -A qcd'
        print '       --SusyBench to specify which of the preset benchmarks to generate (default 2)'
        print '       --mass or -m to set HNL or New Particle mass'
        print '       --couplings \'U2e,U2mu,U2tau\' or -c \'U2e,U2mu,U2tau\' to set list of HNL couplings'
        print '       --epsilon value or -e value to set mixing parameter epsilon' 
        print '                   Note that for RPVSUSY the third entry of the couplings is the stop mass'
        sys.exit(2)
for o, a in opts:
        if o in ("-D","--display"):
            eventDisplay = True
        if o in ("--Pythia6",):
            simEngine = "Pythia6"
        if o in ("--Pythia8",):
            simEngine = "Pythia8"
        if o in ("--PG",):
            simEngine = "PG"
        if o in ("-A",):
            inclusive = a
            if a=='b': inputFile = "/eos/experiment/ship/data/Beauty/Cascade-run0-19-parp16-MSTP82-1-MSEL5-5338Bpot.root"
            if a.lower() == 'charmonly':
               charmonly = True
               HNL = False 
            if a not in ['b','c','meson','pbrem','qcd']: inclusive = True
        if o in ("--Genie",):
            simEngine = "Genie"
        if o in ("--NuRadio",):
            simEngine = "nuRadiography"
        if o in ("--Ntuple",):
            simEngine = "Ntuple"
        if o in ("--FollowMuon",):
            followMuon = True
        if o in ("--FastMuon",):
            fastMuon = True
        if o in ("--MuonBack",):
            simEngine = "MuonBack"
        if o in ("--Nuage",):
            simEngine = "Nuage"
        if o in ("--phiRandom",):
            phiRandom = True
        if o in ("--Cosmics",):
            simEngine = "Cosmics"
            Opt_high = 0
            if a!=str(0): Opt_high = int(a)
        if o in ("--MuDIS",):
            simEngine = "muonDIS"
        if o in ("-n", "--nEvents",):
            nEvents = int(a)
        if o in ("-i", "--firstEvent",):
            firstEvent = int(a)
        if o in ("-s", "--seed",):
            theSeed = int(a)
        if o in ("-s", "--sameSeed",):
            sameSeed = int(a)
        if o in ("-f",):
            if a.lower() == "none": inputFile = None
            else: inputFile = a
            defaultInputFile = False
        if o in ("-g",):
            geofile = a
        if o in ("-o", "--output",):
            outputDir = a
        if o in ("-Y",): 
            dy = float(a)
        if o in ("--tankDesign",):
            dv = int(a)
        if o in ("--muShieldDesign",):
            ds = int(a)
        if o in ("--nuTauTargetDesign",):
            nud = int(a)
        if o in ("--caloDesign",):
            caloDesign = int(a)
        if o in ("--strawDesign",):
            strawDesign = int(a)
        if o in ("--charm",):
            charm = int(a)
        if o in ("-F",):
            deepCopy = True
        if o in ("--RpvSusy",):
            HNL = False
            RPVSUSY = True
        if o in ("--DarkPhoton",):
            HNL = False
            DarkPhoton = True
        if o in ("--SusyBench",):
            RPVSUSYbench = int(a)
        if o in ("-m", "--mass",):
           if DarkPhoton: theDPmass = float(a)
           else: theMass = float(a)
        if o in ("-c", "--couplings", "--coupling",):
           theCouplings = [float(c) for c in a.split(",")]
        if o in ("-e", "--epsilon",):
           theDPepsilon = float(a)
        if o in ("-t", "--test"):
            inputFile = "../FairShip/files/Cascade-parp16-MSTP82-1-MSEL4-76Mpot_1_5000.root"
            nEvents = 50

#sanity check
if (HNL and RPVSUSY) or (HNL and DarkPhoton) or (DarkPhoton and RPVSUSY): 
 print "cannot have HNL and SUSY or DP at the same time, abort"
 sys.exit(2)

if (simEngine == "Genie" or simEngine == "nuRadiography") and defaultInputFile: 
  inputFile = "/eos/experiment/ship/data/GenieEvents/genie-nu_mu.root"
            # "/eos/experiment/ship/data/GenieEvents/genie-nu_mu_bar.root"
if simEngine == "muonDIS" and defaultInputFile:
  print 'input file required if simEngine = muonDIS'
  print " for example -f  /eos/experiment/ship/data/muonDIS/muonDis_1.root"
  sys.exit()
if simEngine == "Nuage" and not inputFile:
 inputFile = 'Numucc.root'

print "FairShip setup for",simEngine,"to produce",nEvents,"events"
if (simEngine == "Ntuple" or simEngine == "MuonBack") and defaultInputFile :
  print 'input file required if simEngine = Ntuple or MuonBack'
  print " for example -f /eos/experiment/ship/data/Mbias/pythia8_Geant4-withCharm_onlyMuons_4magTarget.root"
  sys.exit()
ROOT.gRandom.SetSeed(theSeed)  # this should be propagated via ROOT to Pythia8 and Geant4VMC
shipRoot_conf.configure(0)     # load basic libraries, prepare atexit for python
# - muShieldDesign = 2  # 1=passive 5=active (default) 7=short design+magnetized hadron absorber
# - targetOpt      = 5  # 0=solid   >0 sliced, 5: 5 pieces of tungsten, 4 H20 slits, 17: Mo + W +H2O (default)
#   nuTauTargetDesign = 0 # 0 = TP, 1 = NEW with magnet, 2 = NEW without magnet, 3 = 2018 design
if charm == 0: ship_geo = ConfigRegistry.loadpy("$FAIRSHIP/geometry/geometry_config.py", Yheight = dy, tankDesign = dv, \
                                                muShieldDesign = ds, nuTauTargetDesign=nud, CaloDesign=caloDesign, strawDesign=strawDesign, muShieldGeo=geofile)
else: ship_geo = ConfigRegistry.loadpy("$FAIRSHIP/geometry/charm-geometry_config.py")

# switch off magnetic field to measure muon flux
#ship_geo.muShield.Field = 0.
#ship_geo.EmuMagnet.B = 0.
#ship_geo.tauMudet.B = 0.


# Output file name, add dy to be able to setup geometry with ambiguities.
tag = simEngine+"-"+mcEngine
if charmonly: tag = simEngine+"CharmOnly-"+mcEngine
if eventDisplay: tag = tag+'_D'
if dv > 4 : tag = 'conical.'+tag
elif dy: tag = str(dy)+'.'+tag 
if not os.path.exists(outputDir):
  os.makedirs(outputDir)
outFile = "%s/ship.%s.root" % (outputDir, tag)

# rm older files !!! 
for x in os.listdir(outputDir):
  if not x.find(tag)<0: os.system("rm %s/%s" % (outputDir, x) )
# Parameter file name
parFile="%s/ship.params.%s.root" % (outputDir, tag)

# In general, the following parts need not be touched
# ========================================================================

# -----Timer--------------------------------------------------------
timer = ROOT.TStopwatch()
timer.Start()
# ------------------------------------------------------------------------
# -----Create simulation run----------------------------------------
run = ROOT.FairRunSim()
run.SetName(mcEngine)  # Transport engine
run.SetOutputFile(outFile)  # Output file
run.SetUserConfig("g4Config.C") # user configuration file default g4Config.C 
rtdb = run.GetRuntimeDb() 
# -----Create geometry----------------------------------------------
# import shipMuShield_only as shipDet_conf # special use case for an attempt to convert active shielding geometry for use with FLUKA
# import shipTarget_only as shipDet_conf
if charm!=0: import charmDet_conf as shipDet_conf 
else:        import shipDet_conf

modules = shipDet_conf.configure(run,ship_geo)
# -----Create PrimaryGenerator--------------------------------------
primGen = ROOT.FairPrimaryGenerator()
if simEngine == "Pythia8":
 primGen.SetTarget(ship_geo.target.z0, 0.) 
# -----Pythia8--------------------------------------
 if HNL or RPVSUSY:
  P8gen = ROOT.HNLPythia8Generator()
  import pythia8_conf
  if HNL:
   print 'Generating HNL events of mass %.3f GeV\n'%theMass
   print 'and with couplings=',theCouplings
   pythia8_conf.configure(P8gen,theMass,theCouplings,inclusive,deepCopy)
  if RPVSUSY:
   print 'Generating RPVSUSY events of mass %.3f GeV\n'%theMass
   print 'and with couplings=[%.3f,%.3f]\n'%(theCouplings[0],theCouplings[1])
   print 'and with stop mass=\%.3f GeV\n',theCouplings[2]
   pythia8_conf.configurerpvsusy(P8gen,theMass,[theCouplings[0],theCouplings[1]],
                                theCouplings[2],RPVSUSYbench,'c',deepCopy)
  P8gen.SetSmearBeam(1*u.cm) # finite beam size
  P8gen.SetParameters("ProcessLevel:all = off")
  if ds==7: # short muon shield
   P8gen.SetLmin(44*u.m)
   P8gen.SetLmax(107*u.m)
  if inputFile: 
   ut.checkFileExists(inputFile)
# read from external file
   P8gen.UseExternalFile(inputFile, firstEvent)
 if DarkPhoton:
  P8gen = ROOT.DPPythia8Generator()
  if inclusive=='qcd':
	  P8gen.SetDPId(4900023)
  else:
	  P8gen.SetDPId(9900015)
  import pythia8darkphoton_conf
  passDPconf = pythia8darkphoton_conf.configure(P8gen,theDPmass,theDPepsilon,inclusive,deepCopy)
  if (passDPconf!=1): sys.exit()
  P8gen.SetSmearBeam(1*u.cm) # finite beam size
  if ds==7: # short muon shield
   P8gen.SetLmin(44*u.m)
   P8gen.SetLmax(107*u.m)
 if charmonly:
  ut.checkFileExists(inputFile)
  primGen.SetBeam(0.,0., ship_geo.Box.TX-2., ship_geo.Box.TY-2.) #Uniform distribution in x/y on the target (1 cm of margin at both sides)    
  primGen.SmearVertexXY(True)
  P8gen = ROOT.Pythia8Generator()
  P8gen.UseExternalFile(inputFile, firstEvent)
  if ship_geo.MufluxSpectrometer.muflux == False :
     P8gen.SetTarget("volTarget_1",0.,0.) # will distribute PV inside target, beam offset x=y=0.
  else: 
     print "ERROR: charmonly option should not be used for the muonflux measurement"
     1/0
# pion on proton 500GeV
# P8gen.SetMom(500.*u.GeV)
# P8gen.SetId(-211)
 primGen.AddGenerator(P8gen)
if simEngine == "Pythia6":
# set muon interaction close to decay volume
 primGen.SetTarget(ship_geo.target.z0+ship_geo.muShield.length, 0.) 
# -----Pythia6-------------------------
 test = ROOT.TPythia6() # don't know any other way of forcing to load lib
 P6gen = ROOT.tPythia6Generator()
 P6gen.SetMom(50.*u.GeV)
 P6gen.SetTarget("gamma/mu+","n0") # default "gamma/mu-","p+"
 primGen.AddGenerator(P6gen)
# -----Particle Gun-----------------------
if simEngine == "PG": 
  myPgun = ROOT.FairBoxGenerator(22,1)
  myPgun.SetPRange(10,10.2)
  myPgun.SetPhiRange(0, 360) # // Azimuth angle range [degree]
  myPgun.SetThetaRange(0,0) # // Polar angle in lab system range [degree]
  myPgun.SetXYZ(0.*u.cm, 0.*u.cm, 0.*u.cm) 
  primGen.AddGenerator(myPgun)
  run.SetGenerator(primGen)
# -----muon DIS Background------------------------
if simEngine == "muonDIS":
 ut.checkFileExists(inputFile)
 primGen.SetTarget(0., 0.) 
 DISgen = ROOT.MuDISGenerator()
 #
 # infront of the Vessel  up to tracking station 1,
 mu_start, mu_end = ship_geo.Chamber1.z-ship_geo.chambers.Tub1length-10*u.cm,ship_geo.TrackStation1.z
 print 'MuDIS position info input=',mu_start, mu_end,ship_geo.Chamber1.z,ship_geo.chambers.Tub1length
 DISgen.SetPositions(ship_geo.target.z0, mu_start, mu_end)
 DISgen.Init(inputFile,firstEvent) 
 primGen.AddGenerator(DISgen)
 nEvents = min(nEvents,DISgen.GetNevents())
 print 'Generate ',nEvents,' with DIS input', ' first event',firstEvent
# -----neutrino interactions from nuage------------------------
if simEngine == "Nuage":
 primGen.SetTarget(0., 0.)
 Nuagegen = ROOT.NuageGenerator()
 Nuagegen.EnableExternalDecayer(1) #with 0 external decayer is disable, 1 is enabled
 print 'Nuage position info input=',ship_geo.EmuMagnet.zC-ship_geo.NuTauTarget.zdim, ship_geo.EmuMagnet.zC+ship_geo.NuTauTarget.zdim
 #--------------------------------
 #to Generate neutrino interactions in the whole neutrino target
# Nuagegen.SetPositions(ship_geo.EmuMagnet.zC, ship_geo.NuTauTarget.zC-ship_geo.NuTauTarget.zdim/2, ship_geo.NuTauTarget.zC+ship_geo.NuTauTarget.zdim/2, -ship_geo.NuTauTarget.xdim/2, ship_geo.NuTauTarget.xdim/2, -ship_geo.NuTauTarget.ydim/2, ship_geo.NuTauTarget.ydim/2)
 #--------------------------------
 #to Generate neutrino interactions ONLY in ONE brick
 ntt = 6
 nXcells = 7
 nYcells = 3
 nZcells = ntt -1
 startx = -ship_geo.NuTauTarget.xdim/2 + nXcells*ship_geo.NuTauTarget.BrX
 endx = -ship_geo.NuTauTarget.xdim/2 + (nXcells+1)*ship_geo.NuTauTarget.BrX
 starty = -ship_geo.NuTauTarget.ydim/2 + nYcells*ship_geo.NuTauTarget.BrY 
 endy = - ship_geo.NuTauTarget.ydim/2 + (nYcells+1)*ship_geo.NuTauTarget.BrY
 startz = ship_geo.EmuMagnet.zC - ship_geo.NuTauTarget.zdim/2 + ntt *ship_geo.NuTauTT.TTZ + nZcells * ship_geo.NuTauTarget.CellW
 endz = ship_geo.EmuMagnet.zC - ship_geo.NuTauTarget.zdim/2 + ntt *ship_geo.NuTauTT.TTZ + nZcells * ship_geo.NuTauTarget.CellW + ship_geo.NuTauTarget.BrZ
 Nuagegen.SetPositions(ship_geo.target.z0, startz, endz, startx, endx, starty, endy)
 #--------------------------------
 ut.checkFileExists(inputFile)
 Nuagegen.Init(inputFile,firstEvent)
 primGen.AddGenerator(Nuagegen)
 nEvents = min(nEvents,Nuagegen.GetNevents())
 run.SetPythiaDecayer("DecayConfigNuAge.C")
 print 'Generate ',nEvents,' with Nuage input', ' first event',firstEvent
# -----Neutrino Background------------------------
if simEngine == "Genie":
# Genie
 ut.checkFileExists(inputFile)
 primGen.SetTarget(0., 0.) # do not interfere with GenieGenerator
 Geniegen = ROOT.GenieGenerator()
 Geniegen.Init(inputFile,firstEvent) 
 Geniegen.SetPositions(ship_geo.target.z0, ship_geo.tauMudet.zMudetC-5*u.m, ship_geo.TrackStation2.z)
 primGen.AddGenerator(Geniegen)
 nEvents = min(nEvents,Geniegen.GetNevents())
 run.SetPythiaDecayer("DecayConfigNuAge.C")
 print 'Generate ',nEvents,' with Genie input', ' first event',firstEvent
if simEngine == "nuRadiography":
 ut.checkFileExists(inputFile)
 primGen.SetTarget(0., 0.) # do not interfere with GenieGenerator
 Geniegen = ROOT.GenieGenerator()
 Geniegen.Init(inputFile,firstEvent) 
 # Geniegen.SetPositions(ship_geo.target.z0, ship_geo.target.z0, ship_geo.MuonStation3.z)
 Geniegen.SetPositions(ship_geo.target.z0, ship_geo.tauMudet.zMudetC, ship_geo.MuonStation3.z)
 Geniegen.NuOnly()
 primGen.AddGenerator(Geniegen)
 print 'Generate ',nEvents,' for nuRadiography', ' first event',firstEvent
#  add tungsten to PDG
 pdg = ROOT.TDatabasePDG.Instance()
 pdg.AddParticle('W','Ion', 1.71350e+02, True, 0., 74, 'XXX', 1000741840)
#
 run.SetPythiaDecayer('DecayConfigPy8.C')
 # this requires writing a C macro, would have been easier to do directly in python! 
 # for i in [431,421,411,-431,-421,-411]:
 # ROOT.gMC.SetUserDecay(i) # Force the decay to be done w/external decayer
if simEngine == "Ntuple":
# reading previously processed muon events, [-50m - 50m]
 ut.checkFileExists(inputFile)
 primGen.SetTarget(ship_geo.target.z0+50*u.m,0.)
 Ntuplegen = ROOT.NtupleGenerator()
 Ntuplegen.Init(inputFile,firstEvent)
 primGen.AddGenerator(Ntuplegen)
 nEvents = min(nEvents,Ntuplegen.GetNevents())
 print 'Process ',nEvents,' from input file'
#
if simEngine == "MuonBack":
# reading muon tracks from previous Pythia8/Geant4 simulation with charm replaced by cascade production 
 fileType = ut.checkFileExists(inputFile)
 if fileType == 'tree':
 # 2018 background production 
  primGen.SetTarget(ship_geo.target.z0+70.1225*u.m,0.)
 else:
  primGen.SetTarget(ship_geo.target.z0+50*u.m,0.)
 #
 MuonBackgen = ROOT.MuonBackGenerator()
 MuonBackgen.Init(inputFile,firstEvent,phiRandom)
 MuonBackgen.SetSmearBeam(5 * u.cm) # radius of ring, thickness 8mm
 if sameSeed: MuonBackgen.SetSameSeed(sameSeed)
 primGen.AddGenerator(MuonBackgen)
 nEvents = min(nEvents,MuonBackgen.GetNevents())
 MCTracksWithHitsOnly = True # otherwise, output file becomes too big
 print 'Process ',nEvents,' from input file, with Phi random=',phiRandom, ' with MCTracksWithHitsOnly',MCTracksWithHitsOnly
 if followMuon :  
    fastMuon = True
    modules['Veto'].SetFollowMuon()
 if fastMuon :    modules['Veto'].SetFastMuon()
 #   missing for the above use case, without making muon shield sensitve
 # optional, boost gamma2muon conversion
 # ROOT.kShipMuonsCrossSectionFactor = 100. 
#
if simEngine == "Cosmics":
 primGen.SetTarget(0., 0.)
 Cosmicsgen = ROOT.CosmicsGenerator()
 import CMBG_conf
 CMBG_conf.configure(Cosmicsgen, ship_geo)
 if not Cosmicsgen.Init(Opt_high): 
      print "initialization of cosmic background generator failed ",Opt_high
      sys.exit(0)
 primGen.AddGenerator(Cosmicsgen)
 print 'Process ',nEvents,' Cosmic events'
#
run.SetGenerator(primGen)
# ------------------------------------------------------------------------

#---Store the visualiztion info of the tracks, this make the output file very large!!
#--- Use it only to display but not for production!
if eventDisplay: run.SetStoreTraj(ROOT.kTRUE)
else:            run.SetStoreTraj(ROOT.kFALSE)
# -----Initialize simulation run------------------------------------
run.Init()
gMC = ROOT.TVirtualMC.GetMC()
fStack = gMC.GetStack()
if MCTracksWithHitsOnly:
 fStack.SetMinPoints(1)
 fStack.SetEnergyCut(-100.*u.MeV)
elif MCTracksWithEnergyCutOnly:
 fStack.SetMinPoints(-1)
 fStack.SetEnergyCut(100.*u.MeV)
elif MCTracksWithHitsOrEnergyCut: 
 fStack.SetMinPoints(1)
 fStack.SetEnergyCut(100.*u.MeV)
elif deepCopy: 
 fStack.SetMinPoints(0)
 fStack.SetEnergyCut(0.*u.MeV)

if eventDisplay:
 # Set cuts for storing the trajectories, can only be done after initialization of run (?!)
  trajFilter = ROOT.FairTrajFilter.Instance()
  trajFilter.SetStepSizeCut(1*u.mm);  
  trajFilter.SetVertexCut(-20*u.m, -20*u.m,ship_geo.target.z0-1*u.m, 20*u.m, 20*u.m, 200.*u.m)
  trajFilter.SetMomentumCutP(0.1*u.GeV)
  trajFilter.SetEnergyCut(0., 400.*u.GeV)
  trajFilter.SetStorePrimaries(ROOT.kTRUE)
  trajFilter.SetStoreSecondaries(ROOT.kTRUE)

# The VMC sets the fields using the "/mcDet/setIsLocalMagField true" option in "gconfig/g4config.in"
import geomGeant4
# geomGeant4.setMagnetField() # replaced by VMC, only has effect if /mcDet/setIsLocalMagField  false

# Define extra VMC B fields not already set by the geometry definitions, e.g. a global field,
# any field maps, or defining if any volumes feel only the local or local+global field.
# For now, just keep the fields already defined by the C++ code, i.e comment out the fieldMaker
if hasattr(ship_geo.Bfield,"fieldMap"):
  fieldMaker = geomGeant4.addVMCFields(ship_geo.Bfield.fieldMap, ship_geo.Bfield.z, True)

# Print VMC fields and associated geometry objects
if debug > 0:
 geomGeant4.printVMCFields()
 geomGeant4.printWeightsandFields(onlyWithField = True,\
             exclude=['DecayVolume','Tr1','Tr2','Tr3','Tr4','Veto','Ecal','Hcal','MuonDetector','SplitCal'])
# Plot the field example
#fieldMaker.plotField(1, ROOT.TVector3(-9000.0, 6000.0, 50.0), ROOT.TVector3(-300.0, 300.0, 6.0), 'Bzx.png')
#fieldMaker.plotField(2, ROOT.TVector3(-9000.0, 6000.0, 50.0), ROOT.TVector3(-400.0, 400.0, 6.0), 'Bzy.png')

if inactivateMuonProcesses :
 ROOT.gROOT.ProcessLine('#include "Geant4/G4ProcessTable.hh"')
 mygMC = ROOT.TGeant4.GetMC()
 mygMC.ProcessGeantCommand("/process/inactivate muPairProd")
 mygMC.ProcessGeantCommand("/process/inactivate muBrems")
 mygMC.ProcessGeantCommand("/process/inactivate muIoni")
 mygMC.ProcessGeantCommand("/particle/select mu+")
 mygMC.ProcessGeantCommand("/particle/process/dump")
 gProcessTable = ROOT.G4ProcessTable.GetProcessTable()
 procmu = gProcessTable.FindProcess(ROOT.G4String('muIoni'),ROOT.G4String('mu+'))
 procmu.SetVerboseLevel(2)
# -----Start run----------------------------------------------------
run.Run(nEvents)
# -----Runtime database---------------------------------------------
kParameterMerged = ROOT.kTRUE
parOut = ROOT.FairParRootFileIo(kParameterMerged)
parOut.open(parFile)
rtdb.setOutput(parOut)
rtdb.saveOutput()
rtdb.printParamContexts()
getattr(rtdb,"print")()
# ------------------------------------------------------------------------
run.CreateGeometryFile("%s/geofile_full.%s.root" % (outputDir, tag))
# save ShipGeo dictionary in geofile
import saveBasicParameters
saveBasicParameters.execute("%s/geofile_full.%s.root" % (outputDir, tag),ship_geo)

# checking for overlaps
if checking4overlaps:
 fGeo = ROOT.gGeoManager
 fGeo.SetNmeshPoints(10000)
 fGeo.CheckOverlaps(0.1)  # 1 micron takes 5minutes
 fGeo.PrintOverlaps()
 # check subsystems in more detail
 for x in fGeo.GetTopNode().GetNodes(): 
   x.CheckOverlaps(0.0001)
   fGeo.PrintOverlaps()
# -----Finish-------------------------------------------------------
timer.Stop()
rtime = timer.RealTime()
ctime = timer.CpuTime()
print ' ' 
print "Macro finished succesfully." 
if "P8gen" in globals() : 
	if (HNL): print "number of retries, events without HNL ",P8gen.nrOfRetries()
	elif (DarkPhoton): 
		print "number of retries, events without Dark Photons ",P8gen.nrOfRetries()
		print "total number of dark photons (including multiple meson decays per single collision) ",P8gen.nrOfDP()

print "Output file is ",  outFile 
print "Parameter file is ",parFile
print "Real time ",rtime, " s, CPU time ",ctime,"s"

# remove empty events
if simEngine == "MuonBack":
 tmpFile = outFile+"tmp"
 fin   = ROOT.gROOT.GetListOfFiles()[0]
 t     = fin.cbmsim
 fout  = ROOT.TFile(tmpFile,'recreate')
 sTree = t.CloneTree(0)
 nEvents = 0
 pointContainers = []
 for x in sTree.GetListOfBranches():
   name = x.GetName() 
   if not name.find('Point')<0: pointContainers.append('sTree.'+name+'.GetEntries()') # makes use of convention that all sensitive detectors fill XXXPoint containers
 for n in range(t.GetEntries()):
     rc = t.GetEvent(n)
     empty = True 
     for x in pointContainers:
        if eval(x)>0: empty = False
     if not empty:
        rc = sTree.Fill()
        nEvents+=1
 sTree.AutoSave()
 fout.Close()
 print "removed empty events, left with:", nEvents
 rc1 = os.system("rm  "+outFile)
 rc2 = os.system("mv "+tmpFile+" "+outFile)
 fin.SetWritable(False) # bpyass flush error
# ------------------------------------------------------------------------
import checkMagFields
def visualizeMagFields():
 checkMagFields.run()
def checkOverlapsWithGeant4():
 # after /run/initialize, but prints warning messages, problems with TGeo volume
 mygMC = ROOT.TGeant4.GetMC()
 mygMC.ProcessGeantCommand("/geometry/test/recursion_start 0")
 mygMC.ProcessGeantCommand("/geometry/test/recursion_depth 2")
 mygMC.ProcessGeantCommand("/geometry/test/run")
