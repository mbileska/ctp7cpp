This implementation uses CMSSW_14_1_0_pre5.



To create environment:

- cmssw-el7
- cmsrel CMSSW_14_1_0_pre5/src/
- cd CMSSW_14_1_0_pre5
- cmsenv
- git cms-init
- git cms-addpkg L1Trigger/L1TCaloLayer1
- cd L1Trigger 
- git clone -b L1boosted_133X git@github.com:pallabidas/Run3Ntuplizer.git
- cd ..
- scram b


Implementing the files:

1. Choose a model (V2.2 recommended), enter that folder.
2. mkdir CMSSW_14_1_0_pre5/src/L1Trigger/L1TCaloLayer1/data
3. Copy "WOMBAR-V()/model" into CMSSW_14_1_0_pre5/src/L1Trigger/L1TCaloLayer1/data
4. Replace L1TCaloSummary.cc in CMSSW_14_1_0_pre5/src/L1Trigger/L1TCaloLayer1/plugins
5. Replace simCaloStage2Layer1Summary_cfi in CMSSW_14_1_0_pre5/src/L1Trigger/L1TCaloLayer1/python
6. Replace BoostedJetStudies.cc in CMSSW_14_1_0_pre5/src/L1Trigger/Run3Ntuplizer/plugins/
7. For Event Displays: mkdir CMSSW_14_1_0_pre5/src/L1Trigger/EventDsplay/
8. Copy plotVector.C into CMSSW_14_1_0_pre5/src/L1Trigger/EventDsplay/



Running (remember to cmssw-el7):

1. cd CMSSW_14_1_0_pre5/src/
2. cmsenv
3. scram b
4. cd CMSSW_14_1_0_pre5/src/L1Trigger/Run3Ntuplizer/test/
5. voms-proxy-init -voms cms
6. cmsRun testL1TCaloSummary-ggHBB.py

This produces l1TNtuple-ggHBB.root

Efficiency analysis:

1. Copy l1TNtuple-ggHBB.root to the same directory as controlPlot and efficiency.C
(To change dR you will need to modify BoostedJetStudies.cc and re-run, modify the line:
if(reco::deltaR(jet, recoJet_1)<0.4 && foundL1Jet_1 == 0 ) => if(reco::deltaR(jet, recoJet_1)<0.8 && foundL1Jet_1 == 0 )
default is dR=0.4.
If modifying to dR=0.8, use efficiencyAK8 directory, if not, use efficiencyAK4)
2. g++ -g -Wno-deprecated controlplot.C -o plot.exe -I$ROOTSYS/include -L$ROOTSYS/lib `root-config --cflags` `root-config --libs`
3. ./plot.exe "l1TNtuple-ggHBB.root" "output.root" "all" "100"
4. root
5. .x efficiency.C
This should output an efficiency plot.