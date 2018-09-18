#=========================================================================================================================================
#Script to submit Job Array with the command: bsub -q 1nh -J "muonDISTr$n[1-89]" " simDISTr1.sh $n" to run FairShip simulation  
#
#Run 89 Jobs Arrays , each having size of 100
#==========================================================================================================================================

echo "Starting script."
n=$1  
source /afs/cern.ch/work/p/pvenkova/my_FairShip/FairShipRun/config.sh
OutputPath=/eos/experiment/ship/user/pvenkova/MuonProduction2018/MuonDISVessel/muonDISmuonsTr1
File=muonDis_${n}.root
OutputFile=ship.conical.muonDIS-TGeant4_${n}_${LSB_JOBINDEX}.root
GeoFile=geofile_full.conical.muonDIS-TGeant4.root
NJOBS=100
NTOTAL=50000
N=$[$NTOTAL/$NJOBS]

if [ -f $OutputPath/$OutputFile ]; then
       echo "Target exists, nothing to do."
       exit 0
else
	xrdcp $OutputPath/run_simScript.py .
	python  run_simScript.py --nEvents $N  --firstEvent $[$N*($LSB_JOBINDEX-1)] -f  $OutputPath/$File
	mv ship.conical.muonDIS-TGeant4.root ship.conical.muonDIS-TGeant4_${n}_${LSB_JOBINDEX}.root
	ls
	xrdcp $OutputFile $OutputPath
	rm run_simScript.py
	rm $OutputFile
fi
