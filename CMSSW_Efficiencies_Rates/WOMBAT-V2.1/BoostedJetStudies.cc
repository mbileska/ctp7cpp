// system include files
#include <memory>

#include "TROOT.h"
#include "TTree.h"
#include "TFile.h"
#include "TLorentzVector.h"

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
//#include "FWCore/Framework/interface/EDAnalyzer.h"
#include "FWCore/Framework/interface/one/EDAnalyzer.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include "DataFormats/EcalDigi/interface/EcalDigiCollections.h"
#include "DataFormats/HcalDigi/interface/HcalDigiCollections.h"

#include "DataFormats/L1Trigger/interface/L1EmParticle.h"
#include "DataFormats/L1Trigger/interface/L1EmParticleFwd.h"
#include "DataFormats/L1Trigger/interface/L1JetParticle.h"
#include "DataFormats/L1Trigger/interface/L1JetParticleFwd.h"
#include "DataFormats/L1Trigger/interface/L1EtMissParticle.h"
#include "DataFormats/L1Trigger/interface/L1EtMissParticleFwd.h"

#include "DataFormats/L1CaloTrigger/interface/L1CaloCollections.h"
#include "DataFormats/L1CaloTrigger/interface/L1CaloRegion.h"

#include "DataFormats/Math/interface/LorentzVector.h"

//#include "L1Trigger/Run3Ntuplizer/plugins/helpers.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include "FWCore/ServiceRegistry/interface/Service.h"
#include "FWCore/MessageLogger/interface/MessageLogger.h"

#include "FWCore/Utilities/interface/InputTag.h"
#include "FWCore/ServiceRegistry/interface/Service.h"

#include "CommonTools/UtilAlgos/interface/TFileService.h"

// GCT and RCT data formats
#include "DataFormats/L1CaloTrigger/interface/L1CaloCollections.h"
#include "DataFormats/L1GlobalCaloTrigger/interface/L1GctCollections.h"
#include "DataFormats/TauReco/interface/PFTau.h"
#include "DataFormats/TauReco/interface/PFTauDiscriminator.h"
#include "DataFormats/PatCandidates/interface/PackedCandidate.h"
#include "DataFormats/PatCandidates/interface/Tau.h"
#include "DataFormats/PatCandidates/interface/Jet.h"

#include "DataFormats/L1Trigger/interface/BXVector.h"
#include "DataFormats/L1Trigger/interface/Jet.h"
#include "DataFormats/L1Trigger/interface/Tau.h"
#include "DataFormats/L1Trigger/interface/EtSum.h"

#include "SimDataFormats/GeneratorProducts/interface/GenEventInfoProduct.h"
#include "DataFormats/HepMCCandidate/interface/GenParticle.h"
#include "DataFormats/HepMCCandidate/interface/GenParticleFwd.h"

using namespace l1extra;
using namespace std;

bool compareByPt (l1extra::L1JetParticle i, l1extra::L1JetParticle j) { return(i.pt()>j.pt()); };


float getRecoEtaNew(int caloEta){
  float eta = -999.;
  static bool first = true;
  static double twrEtaValues[42];
  if(first) {
    twrEtaValues[0] = 0;
    for(unsigned int i = 0; i < 20; i++) {
      twrEtaValues[i + 1] = 0.0436 + i * 0.0872;
    }
    twrEtaValues[21] = 1.785;
    twrEtaValues[22] = 1.880;
    twrEtaValues[23] = 1.9865;
    twrEtaValues[24] = 2.1075;
    twrEtaValues[25] = 2.247;
    twrEtaValues[26] = 2.411;
    twrEtaValues[27] = 2.575;
    twrEtaValues[28] = 2.825;
    twrEtaValues[29] = 999.;
    twrEtaValues[30] = (3.15+2.98)/2.;
    twrEtaValues[31] = (3.33+3.15)/2.;
    twrEtaValues[32] = (3.50+3.33)/2.;
    twrEtaValues[33] = (3.68+3.50)/2.;
    twrEtaValues[34] = (3.68+3.85)/2.;
    twrEtaValues[35] = (3.85+4.03)/2.;
    twrEtaValues[36] = (4.03+4.20)/2.;
    twrEtaValues[37] = (4.20+4.38)/2.;
    twrEtaValues[38] = (4.74+4.38*3)/4.;
    twrEtaValues[39] = (4.38+4.74*3)/4.;
    twrEtaValues[40] = (5.21+4.74*3)/4.;
    twrEtaValues[41] = (4.74+5.21*3)/4.;
    first = false;
  }
  uint32_t absCaloEta = abs(caloEta);
  if(absCaloEta <= 41) {
    if(caloEta < 0)
      eta =  -twrEtaValues[absCaloEta];
    else
      eta = +twrEtaValues[absCaloEta];
  }
  return eta;
};

float getRecoPhiNew(int caloPhi){
  float phi = -999.;
  if(caloPhi > 72) phi = +999.;
  uint32_t absCaloPhi = std::abs(caloPhi) - 1;
  if(absCaloPhi < 36)
    phi = (((double) absCaloPhi + 0.5) * 0.0872);
  else
    phi = (-(71.5 - (double) absCaloPhi) * 0.0872);
  return phi;
};

//
// class declaration
//

class BoostedJetStudies : public edm::one::EDAnalyzer<edm::one::SharedResources> {
public:
  explicit BoostedJetStudies(const edm::ParameterSet&);
  ~BoostedJetStudies();

  static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);
  void zeroOutAllVariables();

private:
  void analyze(const edm::Event& evt, const edm::EventSetup& es);      
  virtual void beginJob() override;
  virtual void endJob() override;

//  virtual void beginRun(edm::Run const&, edm::EventSetup const&) override;

  // ----------member data ---------------------------
  edm::EDGetTokenT<EcalTrigPrimDigiCollection> ecalSrc_;
  edm::EDGetTokenT<HcalTrigPrimDigiCollection> hcalSrc_;
  edm::EDGetTokenT<vector<reco::CaloJet> > jetSrc_;
  edm::EDGetTokenT<vector<pat::Jet> > jetSrcAK8_;
  edm::EDGetTokenT<reco::GenParticleCollection> genSrc_;

  edm::EDGetTokenT<BXVector<l1t::Jet>> stage2JetToken_;
  edm::EDGetTokenT<BXVector<l1t::Tau>> stage2TauToken_;
  edm::EDGetTokenT<l1t::EtSumBxCollection> stage2EtSumToken_;
  edm::EDGetTokenT<vector<l1extra::L1JetParticle>> l1BoostedToken_;

  TH1F* nEvents;

  int run, lumi, event;

  double genPt_1, genEta_1, genPhi_1, genM_1, genDR;
  int genId, genMother;
  double recoPt_1, recoEta_1, recoPhi_1;
  double l1Pt_1, l1Eta_1, l1Phi_1;
  double seedPt_1, seedEta_1, seedPhi_1;
  
  int l1NthJet_1;
  int recoNthJet_1;
  int seedNthJet_1;

  double recoPt_;
  std::vector<int> nSubJets, nBHadrons, HFlav;
  std::vector<std::vector<int>> subJetHFlav;
  std::vector<float> tau1, tau2, tau3;

  std::vector<TLorentzVector> *ecalTPGs  = new std::vector<TLorentzVector>;
  std::vector<TLorentzVector> *hcalTPGs  = new std::vector<TLorentzVector>;
  std::vector<TLorentzVector> *l1Jets  = new std::vector<TLorentzVector>;
  std::vector<TLorentzVector> *seed180  = new std::vector<TLorentzVector>;
  std::vector<TLorentzVector> *tauseed  = new std::vector<TLorentzVector>;
  std::vector<TLorentzVector> *ak8Jets  = new std::vector<TLorentzVector>;
  std::vector<TLorentzVector> *subJets  = new std::vector<TLorentzVector>;

  void createBranches(TTree *tree);
  TTree* efficiencyTree;
  TH1F* leadL1Pt;
  TH1F* leadL1Eta;
  TH1F* leadL1Phi;
  TH1F* leadSingleJet;
  TH1F* EtSum_HT;
  TH1F* EtSum_ETMHF;
  edm::Service<TFileService> tfs_;  

};

BoostedJetStudies::BoostedJetStudies(const edm::ParameterSet& iConfig) :
  ecalSrc_(consumes<EcalTrigPrimDigiCollection>( edm::InputTag("l1tCaloLayer1Digis"))),
  hcalSrc_(consumes<HcalTrigPrimDigiCollection>( edm::InputTag("l1tCaloLayer1Digis"))),
  jetSrc_(    consumes<vector<reco::CaloJet> >(iConfig.getParameter<edm::InputTag>("recoJets"))),
  jetSrcAK8_( consumes<vector<pat::Jet> >(iConfig.getParameter<edm::InputTag>("recoJetsAK8"))),
  genSrc_( consumes<reco::GenParticleCollection> (iConfig.getParameter<edm::InputTag>( "genParticles"))),
  stage2JetToken_(consumes<BXVector<l1t::Jet>>( edm::InputTag("caloStage2Digis","Jet","RECO"))),
  stage2TauToken_(consumes<BXVector<l1t::Tau>>( edm::InputTag("caloStage2Digis","Tau","RECO"))),
  stage2EtSumToken_(consumes<l1t::EtSumBxCollection>( edm::InputTag("caloStage2Digis","EtSum","RECO"))),
  l1BoostedToken_(consumes<vector<l1extra::L1JetParticle>>( edm::InputTag("simCaloStage2Layer1Summary","Boosted","")))
{
  // Initialize the Tree

  recoPt_      = iConfig.getParameter<double>("recoPtCut");
  nEvents      = tfs_->make<TH1F>( "nEvents"  , "nEvents", 2,  0., 1. );
  efficiencyTree = tfs_->make<TTree>("efficiencyTree", "Gen Matched Jet Tree ");
  createBranches(efficiencyTree);
  leadL1Pt     = tfs_->make<TH1F>( "leadL1Pt", "leadL1Pt", 100, 0., 1100.);
  leadL1Eta    = tfs_->make<TH1F>( "leadL1Eta", "leadL1Eta", 100, -5., 5.);
  leadL1Phi    = tfs_->make<TH1F>( "leadL1Phi", "leadL1Phi", 100, -M_PI, M_PI);
  leadSingleJet= tfs_->make<TH1F>( "leadSingleJet", "leadSingleJet", 100, 0., 1100.);
  EtSum_HT     = tfs_->make<TH1F>( "EtSum_HT", "EtSum_HT", 100, 0., 1100.);
  EtSum_ETMHF  = tfs_->make<TH1F>( "EtSum_ETMHF", "EtSum_ETMHF", 100, 0., 1100.);
}

BoostedJetStudies::~BoostedJetStudies() {
}

//
// member functions
//

// ------------ method called to produce the data  ------------

void BoostedJetStudies::analyze( const edm::Event& evt, const edm::EventSetup& es )
{
  using namespace edm;

  nEvents->Fill(1);
  run = evt.id().run();
  lumi = evt.id().luminosityBlock();
  event = evt.id().event();
  Handle<L1CaloRegionCollection> regions;
   
  std::vector<reco::CaloJet> goodJets;
  std::vector<pat::Jet> goodJetsAK8;
  std::vector<l1t::Jet> seeds;

  ecalTPGs->clear();
  hcalTPGs->clear();
  l1Jets->clear();
  seed180->clear();
  tauseed->clear();
  ak8Jets->clear();
  subJets->clear();
  nSubJets.clear();
  nBHadrons.clear();
  subJetHFlav.clear();
  tau1.clear();
  tau2.clear();
  tau3.clear();

  edm::Handle<EcalTrigPrimDigiCollection> ecalTPs;
  evt.getByToken(ecalSrc_, ecalTPs);
  for ( const auto& ecalTp : *ecalTPs ) {
    int caloEta = ecalTp.id().ieta();
    int caloPhi = ecalTp.id().iphi();
    int et = ecalTp.compressedEt();
    if(et != 0) {
      float eta = getRecoEtaNew(caloEta);
      float phi = getRecoPhiNew(caloPhi);
      TLorentzVector temp;
      temp.SetPtEtaPhiE(et,eta,phi,et);
      ecalTPGs->push_back(temp);
    }
  }

  edm::Handle<HcalTrigPrimDigiCollection> hcalTPs;
  evt.getByToken(hcalSrc_, hcalTPs);
  for ( const auto& hcalTp : *hcalTPs ) {
    int caloEta = hcalTp.id().ieta();
    uint32_t absCaloEta = abs(caloEta);
    if(absCaloEta == 29) {
      continue;
    }
    else if(hcalTp.id().version() == 0 && absCaloEta > 29) {
      continue;
    }
    else if(absCaloEta <= 41) {
      int caloPhi = hcalTp.id().iphi();
      if(caloPhi <= 72) {
	int et = hcalTp.SOI_compressedEt();
	if(et != 0) {
          float eta = getRecoEtaNew(caloEta);
          float phi = getRecoPhiNew(caloPhi);
          TLorentzVector temp;
          temp.SetPtEtaPhiE(et,eta,phi,et);
          hcalTPGs->push_back(temp);
	}
      }
      else {
	std::cerr << "Illegal Tower: caloEta = " << caloEta << "; caloPhi =" << caloPhi << std::endl;
      }
    }
    else {
      std::cerr << "Illegal Tower: caloEta = " << caloEta << std::endl;
    }
  }

  // Accessing existing L1 seed stored in MINIAOD
  edm::Handle<BXVector<l1t::Jet>> stage2Jets;
  if(!evt.getByToken(stage2JetToken_, stage2Jets)) cout<<"ERROR GETTING THE STAGE 2 JETS"<<std::endl;
  evt.getByToken(stage2JetToken_, stage2Jets);
  const BXVector<l1t::Jet> &s2j = *stage2Jets;
  for(auto obj : s2j) {
    seeds.push_back(obj);
    TLorentzVector temp;
    temp.SetPtEtaPhiE(obj.pt(), obj.eta(), obj.phi(), obj.pt());
    seed180->push_back(temp);
  }
  if(seed180->size() > 0) leadSingleJet->Fill(seed180->at(0).Pt());

  edm::Handle<BXVector<l1t::Tau>> stage2Taus;
  if(!evt.getByToken(stage2TauToken_, stage2Taus)) cout<<"ERROR GETTING THE STAGE 2 TAUS"<<std::endl;
  evt.getByToken(stage2TauToken_, stage2Taus);
  const BXVector<l1t::Tau> &s2t = *stage2Taus;
  for(auto obj : s2t) {
    TLorentzVector temp;
    temp.SetPtEtaPhiE(obj.pt(), obj.eta(), obj.phi(), obj.pt());
    tauseed->push_back(temp);
  }

  edm::Handle<l1t::EtSumBxCollection> stage2EtSum;
  if(!evt.getByToken(stage2EtSumToken_, stage2EtSum)) cout<<"ERROR GETTING THE STAGE 2 ETSUM"<<endl;
  evt.getByToken(stage2EtSumToken_, stage2EtSum);
  for (l1t::EtSumBxCollection::const_iterator obj = stage2EtSum->begin(0); obj != stage2EtSum->end(0); obj++) {
    if(obj->getType() == l1t::EtSum::kTotalHt){
      EtSum_HT->Fill(obj->pt());
    }
    if(obj->getType() == l1t::EtSum::kMissingHtHF){
      EtSum_ETMHF->Fill(obj->pt());
    }
  }

  // Accessing L1boosted collection
  edm::Handle<vector<l1extra::L1JetParticle>> l1Boosted;
  if(!evt.getByToken(l1BoostedToken_, l1Boosted)) cout<<"ERROR GETTING THE L1BOOSTED JETS"<<std::endl;
  evt.getByToken(l1BoostedToken_, l1Boosted);
  const vector<l1extra::L1JetParticle> &l1B = *l1Boosted;
  for(auto obj : l1B) {
    TLorentzVector temp;
    temp.SetPtEtaPhiE(obj.pt(), obj.eta(), obj.phi(), obj.pt());
    l1Jets->push_back(temp);
  }
  if(l1Jets->size() > 0) {
    leadL1Pt->Fill(l1Jets->at(0).Pt());
    leadL1Eta->Fill(l1Jets->at(0).Eta());
    leadL1Phi->Fill(l1Jets->at(0).Phi());
  }

  // Start Runing Analysis
  Handle<vector<reco::CaloJet> > jets;
  if(evt.getByToken(jetSrc_, jets)){//Begin Getting Reco Jets
    for (const reco::CaloJet &jet : *jets) {
      if(jet.pt() > recoPt_ ) {
	goodJets.push_back(jet);
      }
    }
  }
  else
    cout<<"Error getting calo jets"<<std::endl;

  Handle<vector<pat::Jet> > jetsAK8;

  if(evt.getByToken(jetSrcAK8_, jetsAK8)){//Begin Getting AK8 Jets
    for (const pat::Jet &jetAK8 : *jetsAK8) {
      if(jetAK8.pt() > recoPt_ ) {
        nSubJets.push_back(jetAK8.subjets("SoftDropPuppi").size());
        nBHadrons.push_back(jetAK8.jetFlavourInfo().getbHadrons().size());
        TLorentzVector temp ;
        temp.SetPtEtaPhiE(jetAK8.pt(),jetAK8.eta(),jetAK8.phi(),jetAK8.et());
        ak8Jets->push_back(temp);
        if(jetAK8.subjets("SoftDropPuppi").size() ==  2 && jetAK8.jetFlavourInfo().getbHadrons().size() > 1){
          goodJetsAK8.push_back(jetAK8);
        }
      }
    }
  }
  else
    cout<<"Error getting AK8 jets"<<std::endl;

  zeroOutAllVariables();
  if(goodJetsAK8.size()>0){

    for(auto jet:goodJetsAK8){
      tau1.push_back(jet.userFloat("NjettinessAK8Puppi:tau1"));
      tau2.push_back(jet.userFloat("NjettinessAK8Puppi:tau2"));
      tau3.push_back(jet.userFloat("NjettinessAK8Puppi:tau3"));
      HFlav.clear();
      for(unsigned int isub=0; isub<((jet.subjets("SoftDropPuppi")).size()); isub++){
        HFlav.push_back(jet.subjets("SoftDropPuppi")[isub]->hadronFlavour());
        TLorentzVector temp;
        temp.SetPtEtaPhiE(jet.subjets("SoftDropPuppi")[isub]->pt(),jet.subjets("SoftDropPuppi")[isub]->eta(),jet.subjets("SoftDropPuppi")[isub]->phi(),jet.subjets("SoftDropPuppi")[isub]->et());
        subJets->push_back(temp);
      }
      subJetHFlav.push_back(HFlav);
      //take more variables from here: https://github.com/gouskos/HiggsToBBNtupleProducerTool/blob/opendata_80X/NtupleAK8/src/FatJetInfoFiller.cc#L215-L217
      // https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideBTagMCTools
    }

    //Match to boosted jets and see if we can match subjettiness functions...
    vector<l1extra::L1JetParticle> l1JetsSorted;
    for( vector<l1extra::L1JetParticle>::const_iterator l1Jet = l1Boosted->begin(); l1Jet != l1Boosted->end(); l1Jet++ ){
      l1JetsSorted.push_back(*l1Jet);
    }
    if(l1JetsSorted.size() > 1){  std::sort(l1JetsSorted.begin(),l1JetsSorted.end(),compareByPt);}

    pat::Jet recoJet_1;

    recoPt_1  = goodJetsAK8.at(0).pt();
    recoEta_1 = goodJetsAK8.at(0).eta();
    recoPhi_1 = goodJetsAK8.at(0).phi();
    recoJet_1 = goodJetsAK8.at(0);

    int i = 0;
    int foundL1Jet_1 = 0;
    l1extra::L1JetParticle l1Jet_1;
    if(l1JetsSorted.size() > 0){
      for(auto jet : l1JetsSorted){
        if(reco::deltaR(jet, recoJet_1)<0.4 && foundL1Jet_1 == 0 ){
          l1Jet_1 = jet;
          l1Pt_1  = jet.pt();
          l1Eta_1 = jet.eta();
          l1Phi_1 = jet.phi();
          l1NthJet_1 = i;
          foundL1Jet_1 = 1;
        }
        i++;
      }
    }

    int j = 0;
    int foundSeed_1 = 0;
    if(seeds.size() > 0){
      for(auto seed : seeds){
        if(reco::deltaR(seed, recoJet_1)<0.4 && foundSeed_1 == 0 ){
          seedPt_1  = seed.pt();
          seedEta_1 = seed.eta();
          seedPhi_1 = seed.phi();
          seedNthJet_1 = j;
          foundSeed_1 = 1;
        }
        j++;
      }
    }

  }

  edm::Handle<reco::GenParticleCollection> genParticles;
  if(evt.getByToken(genSrc_, genParticles)){//Begin Getting Gen Particles
    for (reco::GenParticleCollection::const_iterator genparticle = genParticles->begin(); genparticle != genParticles->end(); genparticle++){
      double DR = reco::deltaR(recoEta_1, recoPhi_1, genparticle->eta(), genparticle->phi());
      if (DR < genDR && genparticle->status() > 21 && genparticle->status() < 41){
        genDR = DR;
        genId = genparticle->pdgId();
        genMother = genparticle->motherRef(0)->pdgId();
        genPt_1 = genparticle->pt();
        genEta_1 = genparticle->eta();
        genPhi_1 = genparticle->phi();
        genM_1 = genparticle->mass();
      }
    }
  }
  efficiencyTree->Fill();
}

void BoostedJetStudies::zeroOutAllVariables(){
  genPt_1=-99; genEta_1=-99; genPhi_1=-99; genM_1=-99; genDR=99; genId=-99; genMother=-99;
  seedPt_1=-99; seedEta_1=-99; seedPhi_1=-99; seedNthJet_1=-99;
  recoPt_1=-99; recoEta_1=-99; recoPhi_1=-99; recoNthJet_1=-99;
  l1Pt_1=-99; l1Eta_1=-99; l1Phi_1=-99; l1NthJet_1=-99;
  recoPt_=-99;
}

void BoostedJetStudies::createBranches(TTree *tree){
    tree->Branch("run",     &run,     "run/I");
    tree->Branch("lumi",    &lumi,    "lumi/I");
    tree->Branch("event",   &event,   "event/I");
    tree->Branch("genPt_1",       &genPt_1,     "genPt_1/D");
    tree->Branch("genEta_1",      &genEta_1,    "genEta_1/D");
    tree->Branch("genPhi_1",      &genPhi_1,    "genPhi_1/D");
    tree->Branch("genM_1",        &genM_1,      "genM_1/D");
    tree->Branch("genDR",         &genDR,       "genDR/D");
    tree->Branch("genId",         &genId,       "genId/I");
    tree->Branch("genMother",     &genMother,   "genMother/I");
    tree->Branch("seedPt_1",      &seedPt_1,     "seedPt_1/D");
    tree->Branch("seedEta_1",     &seedEta_1,    "seedEta_1/D");
    tree->Branch("seedPhi_1",     &seedPhi_1,    "seedPhi_1/D");
    tree->Branch("seedNthJet_1",  &seedNthJet_1, "seedNthJet_1/I");
    tree->Branch("recoPt_1",      &recoPt_1,     "recoPt_1/D");
    tree->Branch("recoEta_1",     &recoEta_1,    "recoEta_1/D");
    tree->Branch("recoPhi_1",     &recoPhi_1,    "recoPhi_1/D");
    tree->Branch("recoNthJet_1",  &recoNthJet_1, "recoNthJet_1/I");
    tree->Branch("l1Pt_1",        &l1Pt_1,       "l1Pt_1/D"); 
    tree->Branch("l1Eta_1",       &l1Eta_1,      "l1Eta_1/D");
    tree->Branch("l1Phi_1",       &l1Phi_1,      "l1Phi_1/D");
    tree->Branch("l1NthJet_1",    &l1NthJet_1,   "l1NthJet_1/I");
    tree->Branch("tau1",          &tau1);
    tree->Branch("tau2",          &tau2);
    tree->Branch("tau3",          &tau3);
    tree->Branch("nSubJets",      &nSubJets);
    tree->Branch("subJetHFlav",   &subJetHFlav);
    tree->Branch("nBHadrons",     &nBHadrons);
    tree->Branch("ecalTPGs", "vector<TLorentzVector>", &ecalTPGs, 32000, 0);
    tree->Branch("hcalTPGs", "vector<TLorentzVector>", &hcalTPGs, 32000, 0);
    tree->Branch("l1Jets", "vector<TLorentzVector>", &l1Jets, 32000, 0);
    tree->Branch("seed180", "vector<TLorentzVector>", &seed180, 32000, 0);
    tree->Branch("tauseed", "vector<TLorentzVector>", &tauseed, 32000, 0);
    tree->Branch("ak8Jets", "vector<TLorentzVector>", &ak8Jets, 32000, 0);
    tree->Branch("subJets", "vector<TLorentzVector>", &subJets, 32000, 0);
  }


// ------------ method called once each job just before starting event loop  ------------
void 
BoostedJetStudies::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
void 
BoostedJetStudies::endJob() {
}

// ------------ method called when starting to processes a run  ------------

//void
//BoostedJetStudies::beginRun(edm::Run const& iRun, edm::EventSetup const& iSetup) {
//}
 
// ------------ method called when ending the processing of a run  ------------
/*
  void
  BoostedJetStudies::endRun(edm::Run const&, edm::EventSetup const&)
  {
  }
*/
 
// ------------ method called when starting to processes a luminosity block  ------------
/*
  void
  BoostedJetStudies::beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
  {
  }
*/
 
// ------------ method called when ending the processing of a luminosity block  ------------
/*
  void
  BoostedJetStudies::endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
  {
  }
*/
 
// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
BoostedJetStudies::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(BoostedJetStudies);
