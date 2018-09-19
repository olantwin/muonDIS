echo "Starting script."
source /afs/cern.ch/work/p/pvenkova/my_FairShip/FairShipRun/config.sh 

n="$1"

InputPath=/eos/experiment/ship/user/pvenkova/MuonProduction2018/MuonBackCavern
InputFile=ship.conical.MuonBack-TGeant4_${n}_${LSB_JOBINDEX}.root
OutputFile=muonsNewProduction_${n}_${LSB_JOBINDEX}.root
GeoFile=geofile_full.conical.MuonBack-TGeant4.root
OutputPath=/afs/cern.ch/work/p/pvenkova/Muonprod-2018

if [ $LSB_JOBINDEX -eq 1 ]; then
	InputFile=ship.conical.MuonBack-TGeant4_0.root
	OutputFile=muonsNewProduction_0.root
fi
if [ $LSB_JOBINDEX -eq 66 ]; then 
	InputFile=ship.conical.MuonBack-TGeant4_1000.root
	OutputFile=muonsNewProduction_1000.root
fi


if [ -f $OutputPath/$OutputFile ]; then
       echo "Target exists, nothing to do."
       exit 0
else
	python $OutputPath/make -f $InputPath/$InputFile -g $InputPath/$GeoFile
	mv muonsNewProduction.root $OutputFile
	xrdcp $OutputFile $OutputPath
fi

#I saved it on my afs space the otputfiles. 
#hadd -f muonsCavern2018.0-66000.roo muonsNewProduction_* 
