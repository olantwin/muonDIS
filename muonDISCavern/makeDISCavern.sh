#bsub -q 1nd -J "MDVessel[1-101]"
echo "Starting script."
source /afs/cern.ch/work/p/pvenkova/my_FairShip/FairShipRun/config.sh 
File=makeMuonDIS.py
InputFile=muonsCavern2018.0-66000.root
InputPath=/eos/experiment/ship/user/pvenkova/MuonProduction2018/MuonBackCavern
OutputPath=/eos/experiment/ship/user/pvenkova/MuonProduction2018/MuonBackCavern/muonDISCavern
OutputFile=muonDis_${LSB_JOBINDEX}.root
N=2087
#JOBS=20000

if [ -f $OutputPath/$OutputFile ]; then
       echo "Target exists, nothing to do."
       exit 0
else
		xrdcp $InputPath/$InputFile .
		python /afs/cern.ch/work/p/pvenkova/Muonprod-2018/$File -f $InputPath/$InputFile -nPerJobs $N -nJobs $LSB_JOBINDEX  -nDISPerMuon 1 
		xrdcp $OutputFile $OutputPath
		rm  $OutputFile
		rm $InputFile
fi
