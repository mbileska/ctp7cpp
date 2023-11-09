#define maketv_cxx
#include "maketv.h"
#include <TH2.h>
#include <TStyle.h>
#include <TCanvas.h>

void maketv::Loop()
{
//   In a ROOT session, you can do:
//      root> .L maketv.C
//      root> maketv t
//      root> t.GetEntry(12); // Fill t data members with entry number 12
//      root> t.Show();       // Show values of entry 12
//      root> t.Show(16);     // Read and show values of entry 16
//      root> t.Loop();       // Loop on all entries
//
//     ntuple from /afs/cern.ch/work/p/pdas/Run3Ntuplizer/fromSridhara/CMSSW_11_2_0/src/edanalyzer/L1TRegionDumper/test/

//     This is the loop skeleton where:
//    jentry is the global entry number in the chain
//    ientry is the entry number in the current Tree
//  Note that the argument to GetEntry must be:
//    jentry for TChain::GetEntry
//    ientry for TTree::GetEntry and TBranch::GetEntry
//
//       To read only selected branches, Insert statements like:
// METHOD1:
//    fChain->SetBranchStatus("*",0);  // disable all branches
//    fChain->SetBranchStatus("branchname",1);  // activate branchname
// METHOD2: replace line
//    fChain->GetEntry(jentry);       //read all branches
//by  b_branchname->GetEntry(ientry); //read only this branch
   if (fChain == 0) return;

   Long64_t nentries = fChain->GetEntriesFast();

   Long64_t nbytes = 0, nb = 0;

   ofstream myfile;
   myfile.open ("testVector_realistic_Events.txt");
   myfile << "=====================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================";
   myfile << "\n";
   myfile << "WordCnt\tLINK_00         LINK_01         LINK_02         LINK_03         LINK_04         LINK_05         LINK_06         LINK_07         LINK_08         LINK_09         LINK_10         LINK_11         LINK_12         LINK_13         LINK_14         LINK_15         LINK_16         LINK_17         LINK_18         LINK_19         LINK_20         LINK_21         LINK_22         LINK_23         LINK_24         LINK_25         LINK_26         LINK_27         LINK_28         LINK_29         LINK_30         LINK_31         LINK_32         LINK_33         LINK_34         LINK_35";
   myfile << "\n";
   myfile << "#BeginData";
   myfile << "\n";
   uint16_t eWord[252] = {0};
   unsigned short count = 0;

   for (Long64_t jentry=0; jentry<nentries;jentry++) {
   //for (Long64_t jentry=0; jentry<256;jentry++) {
      Long64_t ientry = LoadTree(jentry);
      if (ientry < 0) break;
      nb = fChain->GetEntry(jentry);   nbytes += nb;
      // if (Cut(ientry) < 0) continue;
      for(int i=0; i<252; i++){
         eWord[i] = cregions->at(i);
      }
      for(int cyc=0; cyc<4; cyc++){
         myfile << "0x" << std::hex << std::setfill('0') << std::setw(4) << count << "\t";
         for(int i=0; i<36; i++){
            if(cyc==0) myfile << "0x" << std::hex << std::setfill('0') << std::setw(2) << (0XFF & eWord[i*7+1]) << std::setw(4) << eWord[i*7] << "00\t";
            if(cyc==1) myfile << "0x" << std::hex << std::setfill('0') << std::setw(2) << (0XFF & eWord[i*7+3]) << std::setw(4) << eWord[i*7+2] << std::setfill('0') << std::setw(2) << ( 0xFF & (eWord[i*7+1] >> 8)) <<"\t";
            if(cyc==2) myfile << "0x" << std::hex << std::setfill('0') << std::setw(2) << (0XFF & eWord[i*7+5]) << std::setw(4) << eWord[i*7+4] << std::setfill('0') << std::setw(2) << ( 0xFF & (eWord[i*7+3] >> 8)) <<"\t";
            if(cyc==3) myfile << "0x00" << std::hex << std::setfill('0') << std::setw(4) << eWord[i*7+6] << std::setfill('0') << std::setw(2) << ( 0xFF & (eWord[i*7+5] >> 8)) <<"\t";
         }
         count++;
         myfile << "\n";
      }
   }
   myfile.close();

}
