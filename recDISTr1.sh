
#=========================================================================================================================================
#Script to submit Job Array with the command: bsub -q 1nh -J "muonDISTr[1-89]" < recDISTr1.sh to run reconstruction 
#
#==========================================================================================================================================
source /afs/cern.ch/work/p/pvenkova/my_FairShip/FairShipRun/config.sh
OutputPath=/eos/experiment/ship/user/pvenkova/MuonProduction2018/MuonDISVessel/muonDISmuonsTr1
File=ship.conical.muonDIS-TGeant4_${LSB_JOBINDEX}.root
GeoFile=geofile_full.conical.muonDIS-TGeant4.root

if [ -f $OutputPath/ship.conical.muonDIS-TGeant4_${LSB_JOBINDEX}_rec.root   ]; then
       echo "Target exists, nothing to do."
       exit 0
else

	xrdcp $OutputPath/$File .
	xrdcp /eos/experiment/ship/user/pvenkova/MuonProduction2018/MuonDISVessel/$GeoFile .
	python  $FAIRSHIP/macro/ShipReco.py -f $File -g $GeoFile
	ls
	mv ship.conical.muonDIS-TGeant4_${LSB_JOBINDEX}_rec.root $OutputPath
	rm $GeoFile
fi
