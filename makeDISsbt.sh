#bsub -q 1nd -J "MDVessel[1-101]"
echo "Starting script."
source /afs/cern.ch/work/p/pvenkova/my_FairShip/FairShipRun/config.sh 
InputPath=/afs/cern.ch/work/p/pvenkova/Muonprod-2018/muonDISSBT
File=makeMuonDIS.py
InputFile=muonsNewProduction.root
OutputPath=/eos/experiment/ship/user/pvenkova/MuonProduction2018/MuonDISVessel
OutputFile=muonDis_${LSB_JOBINDEX}.root
nEvent=907
nIndex=9
N=$[$nEvent/$nIndex]

if [ -f $InputPath/$OutputFile ]; then
       echo "Target exists, nothing to do."
       exit 0
else
	if (($LSB_JOBINDEX == "100" ));then
		python $InputPath/$File -f $OutputPath/$InputFile -nPerJobs 9 -nJobs 0   -nDISPerMuon 1000
		xrdcp muonDis_0.root $OutputPath
		rm muonDis_0.root

	else
		python $InputPath/$File -f $OutputPath/$InputFile -nPerJobs 9 -nJobs $LSB_JOBINDEX  -nDISPerMuon 1000 > out_${LSB_JOBINDEX}
		xrdcp $OutputFile $InputPath
		xrdcp out_${LSB_JOBINDEX} $InputPath
		rm  $OutputFile

		rm out_${LSB_JOBINDEX}
	fi
fi
