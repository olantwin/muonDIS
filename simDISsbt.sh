echo "Starting script."
n=$1
source /afs/cern.ch/work/p/pvenkova/my_FairShip/FairShipRun/config.sh
#OutPath=/eos/experiment/ship/user/pvenkova/MuonProduction2018/MuonDISVessel
OutPath=/eos/experiment/ship/user/pvenkova/MuonProduction2018/MuonDISVessel/test_deactiveMuonNuclear
InputPath=/afs/cern.ch/work/p/pvenkova/Muonprod-2018/muonDISSBT
File=muonDis_${n}.root
OutputFile=ship.conical.muonDIS-TGeant4_${n}_${LSB_JOBINDEX}.root
GeoFile=geofile_full.conical.muonDIS-TGeant4.root
NJOBS=100
NTOTAL=9000
#NTOTAL=1800
N=$[$NTOTAL/$NJOBS]
if (($n == "100" ));then
	File=muonDis_100.root
	NJOBS=9
	NTOTAL=7000
        #N=$[$N+$NTOTAL%$NJOBS]
	N=70
	echo "The number of events for 0 muonDIS:", $N
fi

#if [ -f $InputPath/$OutputFile ]; then
#       echo "Target exists, nothing to do."
#       exit 0
#else
xrdcp $FAIRSHIP/macro/run_simScript.py .
#xrdcp /afs/cern.ch/work/p/pvenkova/Muonprod-2018/muonDISSBT/$File . 

python  $FAIRSHIP/macro/run_simScript.py --nEvents $N  --firstEvent $[$N*($LSB_JOBINDEX-1)] -f  $InputPath/$File
echo "The First event=", $[$N*($LSB_JOBINDEX-1)]
echo "The N of events=", $N
mv ship.conical.muonDIS-TGeant4.root ship.conical.muonDIS-TGeant4_${n}_${LSB_JOBINDEX}.root
ls
xrdcp $OutputFile $OutPath
#rm $InputFile
#fi
