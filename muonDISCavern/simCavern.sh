!/bin/sh
#BSUB -q 8nh
echo "Starting script."
source /afs/cern.ch/work/p/pvenkova/my_FairShip/FairShipRun/config.sh 

NF=$1 #index in the name of the file 
NTOTAL=$2 #number of events in file, the number of events is different for different files, read it from file  
InputPath=/eos/experiment/ship/data/Mbias/background-prod-2018/
OutputPath=/eos/experiment/ship/user/pvenkova/MuonProduction2018/MuonBackCavern
InputFile=pythia8_Geant4_10.0_withCharmandBeauty${NF}_mu.root
OutputFile=ship.conical.MuonBack-TGeant4_${NF}_${LSB_JOBINDEX}.root
GeoFile=geofile_full.conical.MuonBack-TGeant4.root
NJOBS=6
N=$[$NTOTAL/$NJOBS]
if [ $LSB_JOBINDEX -eq $NJOBS ]; then
        N=$[$N+$NTOTAL%$NJOBS]
fi

if [ -f $OutputPath/$OutputFile ]; then
       echo "Target exists, nothing to do."
       exit 0
else
       echo "everything is correct , Now I am  executing  it"

       xrdcp $InputPath/$InputFile .
       python $FAIRSHIP/macro/run_simScript.py --MuonBack -f $InputFile --FastMuon --FollowMuon --nEvents $N --firstEvent $[$N*($LSB_JOBINDEX-1)] 
       mv  ship.conical.MuonBack-TGeant4.root $OutputFile
       mv  $OutputFile $OutputPath
       rm  $InputFile
fi

if [ $NF -eq 1 ]; then
   xrdcp $GeoFile $OutputPath

fi

