#=========================================================================================================================================
#                   Script to submit Job Array with the command: bsub -q 1nh -J "muonDISTr1[1-89]" < makeDISTr1.sh  
#
#==========================================================================================================================================

echo "Starting script"
source /afs/cern.ch/work/p/pvenkova/my_FairShip/FairShipRun/config.sh 
InputPath=/eos/experiment/ship/user/pvenkova/MuonProduction2018/MuonDISVessel/muonDISmuonsTr1
File=makeMuonDIS.py
InputFile=muonsNewProductionTr1.root
OutputPath=/eos/experiment/ship/user/pvenkova/MuonProduction2018/MuonDISVessel/muonDISmuonsTr1
OutputFile=muonDis_${LSB_JOBINDEX}.root
nEvent=445 # number of muons in the InputFule
nIndex=89  # the size of the Job Array , ${LSB_JOBINDEX}
N=$[$nEvent/$nIndex] 

if [ -f $OutputPath/$OutputFile ]; then
       	echo "Target exists, nothing to do."
	exit 0
else
	if (($LSB_JOBINDEX == "89" ));then

		python $InputPath/$File -f $InputPath/$InputFile -nPerJobs 5 -nJobs 0  -nDISPerMuon 10000 
		mv =muonDis_0.root muonDis_${LSB_JOBINDEX}.root
		xrdcp $OutputFile $OutputPath
		rm  $OutputFile
		
	else
		python $InputPath/$File -f $InputPath/$InputFile -nPerJobs 5 -nJobs $LSB_JOBINDEX  -nDISPerMuon 10000 
		xrdcp $OutputFile $OutputPath
		rm  $OutputFile
	fi
if
