//////////////////////////////////////////////////////////
// This class has been automatically generated on
// Tue Feb 18 15:14:21 2020 by ROOT version 6.14/09
// from TTree efficiencyTree/Reco Matched Jet Tree 
// found on file: l1TNtuple-ZeroBias_test.root
//////////////////////////////////////////////////////////

#ifndef controlplot_h
#define controlplot_h

#include <TROOT.h>
#include <TChain.h>
#include <TFile.h>
#include <TH1F.h>
#include <TH2F.h>
#include <TLorentzVector.h>
#include <string>
#include <iostream>
#include <fstream>
#include <TMap.h>
#include <vector>
//#ifdef __MAKECINT__
//#pragma link C++ class vector<std::vector<int> >+;
//#pragma link C++ class vector<std::vector<std::string> >+;
//#pragma link C++ class vector<std::vector<float> >+;
//#pragma link C++ class vector<std::vector<bool> >+;
//#pragma extra_include "vector";
//#endif

using namespace std;

// Header file for the classes stored in the TTree if any.

class controlplot {
public :
   TTree          *fChain;   //!pointer to the analyzed TTree or TChain
   Int_t           fCurrent; //!current Tree number in a TChain
 
   TFile *fileName;
TH1F *recojetpt_eff_den1, *recojetpt_eff_num1,*seedjetpt_eff_den1, *seedjetpt_eff_num1, *recojeteta_eff_den1, *recojeteta_eff_num1, *recojetphi_eff_den1, *recojetphi_eff_num1, *l1jetpt, *l1jetpt_rate1, *seedpt, *seedpt_eff_num1, *seedpt_eff_den1;

// Fixed size dimensions of array or collections stored in the TTree if any.

   // Declaration of leaf types
   Int_t           run;
   Int_t           lumi;
   Int_t           event;
   Double_t        genDR;
   Int_t           genId;
   Double_t        recoPt_1;
   Double_t        recoEta_1;
   Double_t        recoPhi_1;
   Int_t           recoNthJet_1;

   Double_t        l1Pt_1;
   Double_t        l1Eta_1;
   Double_t        l1Phi_1;
   Int_t           l1NthJet_1;
   Double_t        seedPt_1;

   vector<float>   *tau1;
   vector<float>   *tau2;
   vector<float>   *tau3;
   vector<int>     *nSubJets;
   vector<vector<int> > *subJetHFlav;
   vector<int>     *nBHadrons;

   vector<TLorentzVector> *l1Jets;
   vector<TLorentzVector> *ak8Jets;
   vector<TLorentzVector> *subJets;

   // List of branches
   TBranch        *b_run;   //!
   TBranch        *b_lumi;   //!
   TBranch        *b_event;   //!
   TBranch        *b_genDR;   //!
   TBranch        *b_genId;   //!
   TBranch        *b_recoPt_1;   //!
   TBranch        *b_recoEta_1;   //!
   TBranch        *b_recoPhi_1;   //!
   TBranch        *b_recoNthJet_1;   //!

   TBranch        *b_l1Pt_1;   //!
   TBranch        *b_l1Eta_1;   //!
   TBranch        *b_l1Phi_1;   //!
   TBranch        *b_l1NthJet_1;   //!
   TBranch        *b_seedPt_1;

   TBranch        *b_tau1;   //!
   TBranch        *b_tau2;   //!
   TBranch        *b_tau3;   //!
   TBranch        *b_nSubJets;   //!
   TBranch        *b_subJetHFlav;   //!
   TBranch        *b_nBHadrons;   //!

   TBranch        *b_l1Jets;   //!
   TBranch        *b_ak8Jets;   //!
   TBranch        *b_subJets;   //!

   controlplot(const char* file1, const char* file2, const char* recoeta, const char* l1pt);
   virtual ~controlplot();
   virtual Int_t    Cut(Long64_t entry);
   virtual Int_t    GetEntry(Long64_t entry);
   virtual Long64_t LoadTree(Long64_t entry);
   virtual void     Init(TTree *tree);
   virtual void     Loop(const char* recoeta, const char* l1pt);
   virtual Bool_t   Notify();
   virtual void     Show(Long64_t entry = -1);
   virtual void     BookHistos(const char* file2);
};

#endif

#ifdef controlplot_cxx
controlplot::controlplot(const char* file1, const char* file2, const char* recoeta, const char* l1pt)
{
      //  std::cout << "Initializing controlplot..." << std::endl;

   BookHistos(file2);
   TChain *chain = new TChain("l1NtupleProducer/efficiencyTree");
   // ifstream file;
   // file.open(file1, ifstream::in );
   char filename[2000] = "l1TNtuple-ggHBB.root";
   // while (true) {
   //    file >> filename;
   //    if( file.eof() ) break;
         chain->Add(filename);
         cout<<"Added "<<filename<<endl;
   // }//loop over while
   Init(chain);

   //BookHistos(file2);
   //TChain *chain = new TChain("l1NtupleProducer/efficiencyTree");
   //chain->Add(file1);
   //  if(fChain)
   //      std::cout << "fChain initialized successfully." << std::endl;
   //  else
   //      std::cout << "Error initializing fChain." << std::endl;


}

controlplot::~controlplot()
{
   if (!fChain) return;
   delete fChain->GetCurrentFile();
   fileName->cd();
   fileName->Write();
   fileName->Close();
}

Int_t controlplot::GetEntry(Long64_t entry)
{
// Read contents of entry.
   if (!fChain) return 0;
   return fChain->GetEntry(entry);
}
Long64_t controlplot::LoadTree(Long64_t entry)
{
// Set the environment to read one entry
   if (!fChain) return -5;
   Long64_t centry = fChain->LoadTree(entry);
   if (centry < 0) return centry;
   if (fChain->GetTreeNumber() != fCurrent) {
      fCurrent = fChain->GetTreeNumber();
      Notify();
   }
   return centry;
}

void controlplot::Init(TTree *tree)
{
   // The Init() function is called when the selector needs to initialize
   // a new tree or chain. Typically here the branch addresses and branch
   // pointers of the tree will be set.
   // It is normally not necessary to make changes to the generated
   // code, but the routine can be extended by the user if needed.
   // Init() will be called many times when running on PROOF
   // (once per file to be processed).

   // Set object pointer
   tau1 = 0;
   tau2 = 0;
   tau3 = 0;
   nSubJets = 0;
   subJetHFlav = 0;
   nBHadrons = 0;
   l1Jets = 0;
   ak8Jets = 0;
   subJets = 0;

   // Set branch addresses and branch pointers
   if (!tree) return;
   // if (!tree) std::cout << "Init method received nullptr tree." << std::endl;

   fChain = tree;
   fCurrent = -1;
   fChain->SetMakeClass(1);

   fChain->SetBranchAddress("run", &run, &b_run);
   fChain->SetBranchAddress("lumi", &lumi, &b_lumi);
   fChain->SetBranchAddress("event", &event, &b_event);
   fChain->SetBranchAddress("genDR", &genDR, &b_genDR);
   fChain->SetBranchAddress("genId", &genId, &b_genId);
   fChain->SetBranchAddress("recoPt_1", &recoPt_1, &b_recoPt_1);
   fChain->SetBranchAddress("recoEta_1", &recoEta_1, &b_recoEta_1);
   fChain->SetBranchAddress("recoPhi_1", &recoPhi_1, &b_recoPhi_1);
   fChain->SetBranchAddress("recoNthJet_1", &recoNthJet_1, &b_recoNthJet_1);
   fChain->SetBranchAddress("seedPt_1", &seedPt_1, &b_seedPt_1);

   fChain->SetBranchAddress("l1Pt_1", &l1Pt_1, &b_l1Pt_1);
   fChain->SetBranchAddress("l1Eta_1", &l1Eta_1, &b_l1Eta_1);
   fChain->SetBranchAddress("l1Phi_1", &l1Phi_1, &b_l1Phi_1);
   fChain->SetBranchAddress("l1NthJet_1", &l1NthJet_1, &b_l1NthJet_1);

   fChain->SetBranchAddress("tau1", &tau1, &b_tau1);
   fChain->SetBranchAddress("tau2", &tau2, &b_tau2);
   fChain->SetBranchAddress("tau3", &tau3, &b_tau3);
   fChain->SetBranchAddress("nSubJets", &nSubJets, &b_nSubJets);
   fChain->SetBranchAddress("subJetHFlav", &subJetHFlav, &b_subJetHFlav);
   fChain->SetBranchAddress("nBHadrons", &nBHadrons, &b_nBHadrons);
 
   fChain->SetBranchAddress("l1Jets", &l1Jets, &b_l1Jets);
   fChain->SetBranchAddress("ak8Jets", &ak8Jets, &b_ak8Jets);
   fChain->SetBranchAddress("subJets", &subJets, &b_subJets);

   Notify();

}

Bool_t controlplot::Notify()
{
   // The Notify() function is called when a new file is opened. This
   // can be either for a new TTree in a TChain or when when a new TTree
   // is started when using PROOF. It is normally not necessary to make changes
   // to the generated code, but the routine can be extended by the
   // user if needed. The return value is currently not used.

   return kTRUE;
}

void controlplot::Show(Long64_t entry)
{
// Print contents of entry.
// If entry is not specified, print current entry
   if (!fChain) return;
   fChain->Show(entry);
}
Int_t controlplot::Cut(Long64_t entry)
{
// This function may be called from Loop.
// returns  1 if entry is accepted.
// returns -1 otherwise.
   return 1;
}
#endif // #ifdef controlplot_cxx
