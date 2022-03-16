## Files located in <root://eospublic.cern.ch//eos/experiment/ship/user/pvenkova/MuonProduction2018/MuonDISVessel/muonDISmuonsTr1/>

1. `make_nTuple.py`			      : script to produce ntulple with x,y,z,Px,Py,Pz,w  of  muons hitting the Tracking Station 1
2. `muonsNewProductionTr1.root`		      : ntuple with muons hitting the Tracking Station1 
3. `makeMuonDIS.py`			      : script to generate muonDIS interaction with Pythia using the muons hitting the Tr 1 
4. `muonDis_Tr1.root`			      : 445 000 muonDIS interactions ( 445muons*10 000 interactions)
5. `muonDis_*.root`			      : the same content like muonsDis_Tr1.root splited on 89 jobs. Each file contains 5muons*10 000 interactions
6. `run_simScript.py`			      : need it to run FairSHiP simulation, taking as inputFile muonDis_Tr1.root, where the geometry is the 2018 design ( dy':10.,'dv':6,'ds':9,'nud':3,'caloDesign':3,'strawDesign':10)  and the DIS event is placed beetwen the begining of the Vessel until the Tr1, along the muon track according to the material density. 
7. `ship.conical.muonDIS-TGeant4_*.root`	      : outputFile from FairSHiP simulation of muonDIS interactions (89 files, 50 000 events in file)
8. `ship.conical.muonDIS-TGeant4_*_rec.root`    : Reconstructed data (89 files, 50 000 events in file)
9. `geofile_full.conical.muonDIS-TGeant4.root`                                            : file contain the geometry
10. `makeDISTr1.sh`                              : bash script to run Job Array to generate with Pythia6 muonDIS interactions 
11. `simDISTr1.sh`                               : bash script to run Job Array to run FairShip simulation
12. `recDISTr1.sh`                               : bash script to run Job Array to reconstruct 

## Steps for the muonDIS generation in the Vessel using muons hitting the Tr1

1. Run normal Background simulation to select muons hitting the Tr1.  

From the file: 
`/eos/experiment/ship/user/truf/muonBackground-2018/ship.conical.MuonBack-TGeant4-0-66000_rec.root` (obtained using fastMuon, so no EM background,and an intermediate 2018 geometry,produced by Thomas.) 
select  only muons hitting the Tracking Station 1 in the Spectrometer using the code `make_nTuple.py` and save all muons(x,y,z,Px,Py,Pz,w) in the output File
`/eos/experiment/ship/user/pvenkova/MuonProduction2018/MuonDISVessel/muonDISmuonsTr1/muonsNewProductionTr1.root`

The command:

`python make_nTuple.py -f /eos/experiment/ship/user/truf/muonBackground-2018/ship.conical.MuonBack-TGeant4-0-66000_rec.root`

2. Using Pythia6 Generate muon DIS interaction with the selected muons

With each of those  muons generate 10 000 muonDIS interactions and save them in the outputFile: `/eos/experiment/ship/user/pvenkova/MuonProduction2018/MuonDISVessel/muonDISmuonsTr1/muonDis_Tr1.root`

The command:

`python makeMuonDIS.py -f muonsNewProductionTr1.root  -nPerJobs <the number of muons, taken from the inputfile> -nJobs <The index of the job> -nDISPerMuon 10000` 


To run Job Array use the command below, this will produce files  `/eos/experiment/ship/user/pvenkova/MuonProduction2018/MuonDISVessel/muonDISmuonsTr1/muonDis_*.root` (89 files, each contains 50 0000 events) :

`bsub -q 1nh -J "muonDISTr1[1-89]" < makeDISTr1.sh` 

3.Distribute muon DIS  interactions according to the material in the Decay Vessel (FairShip simulation) 


To run Job Array, each having size of 100  use the command below, this will produce files  `/eos/experiment/ship/user/pvenkova/MuonProduction2018/MuonDISVessel/muonDISmuonsTr1/ship.conical.muonDIS-TGeant4_*_*.root`:

`bsub -q 1nh -J "muonDISTr$n[1-89]" " simDISTr1.sh $n"` 
 
4. Reconstuction

To run Job Array  use the command below, this will produce files  `/eos/experiment/ship/user/pvenkova/MuonProduction2018/MuonDISVessel/muonDISmuonsTr1/ship.conical.muonDIS-TGeant4_*_rec.root`:

`bsub -q 1nh -J "muonDISTr[1-89]" < recDISTr1.sh`


## Files located in <root://eospublic.cern.ch//eos/experiment/ship/user/pvenkova/MuonProduction2018/MuonDISVessel>

1. `makentupleSBT.py`  			      : script to produce ntulple with x,y,z,Px,Py,Pz,w  of  muons hitting the SBT
2. `muonsNewProduction.root`		      : ntuple with muons hitting the SBT( 907 muons) 
3. `makeMuonDIS.py`			      : script to generate muonDIS interaction with Pythia using the muons hitting the SBT 
4. `muonDisSbt.root`			      : 907 000 muonDIS interactions ( 907muons*1 000 interactions)
6. `run_simScript.py`			      : need it to run FairSHiP simulation, taking as inputFile `muonDisSbt.root`, where the geometry is the 2018 design ( dy':10.,'dv':6,'ds':9,'nud':3,'caloDesign':3,'strawDesign':10)  and the DIS event is placed beetwen the begining of the Vessel until the Tr1, along the muon track according to the material density. 
7. `ship.conical.muonDIS-TGeant4_*.root`	      : outputFile from FairSHiP simulation of muonDIS interactions (101 files, 9000 events in file)
8. `ship.conical.muonDIS-TGeant4_*_rec.root`    : Reconstructed data (101 files, 9 000 events in file)
9. `geofile_full.conical.muonDIS-TGeant4.root`  : file contain the geometry  
10. `makeDISsbt.sh`                              : bash script to run Job Array to generate with Pythia6 muonDIS interactions 
11. `simDISSst.sh`                               : bash script to run Job Array to run FairShip simulation

## Steps for the muonDIS generation in the Vessel using muons hitting the SBT

For this generations the steps are the same as the one described above.

1. Using the same file `/eos/experiment/ship/user/truf/muonBackground-2018/ship.conical.MuonBack-TGeant4-0-66000_rec.root` collect muons hitting the SBT.

2. Generate muonDIS interaction 

3. FairShiP Simulations

4. Reconstruction

**There is no difference in the software version, geometry or so what ever. The version of the software used to produce both samples is locate on: <https://github.com/Plamenna/FairShip/tree/shipSoft>**
