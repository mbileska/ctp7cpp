#include <iostream>
#include <iomanip>
#include <cmath>
#include <fstream>
#include <new>
#include<climits>
#include "TFile.h"
#include "TTree.h"
#include "TH1.h"
#include "TPad.h"
#include "TCanvas.h"
#include "TH1F.h"
#include "TGraphErrors.h"
#include "TF1.h"
#include "TH2.h"
#include "TProfile.h"

#include "TStyle.h"
#include "TAttFill.h"
#include "TPaveStats.h"
#include "TMinuit.h"
#include "TPostScript.h"
#include "TFitResult.h"
#include "TFitResultPtr.h"
#include "TRandom.h"
#include "TPaletteAxis.h"
#include "TLegend.h"
#include "TLatex.h"
#include "TMath.h"
#include "TCanvas.h"


using namespace std;

void efficiency(){
    TCanvas *c1 =new TCanvas("c1", " ", 0, 0,700,1000);
    c1->Range(0,0,1,1);
    c1->SetFillColor(0);
    c1->SetBorderMode(0);
    c1->SetBorderSize(2);
    c1->SetFrameBorderMode(0);
    c1->Draw();
    c1->SetGrid();
    gStyle->SetOptStat(0);

    TFile *g1 =TFile::Open("output.root");
    TH1F *h1 = (TH1F*)g1->Get("recojetpt_eff_den1");
    TH1F *h2 = (TH1F*)g1->Get("recojetpt_eff_num1");

    TH1F *h3 = (TH1F*)g1->Get("seedjetpt_eff_den1");
    TH1F *h4 = (TH1F*)g1->Get("seedjetpt_eff_num1");
    int rebinFactor = 2; // Change this number as needed
    h1->Rebin(rebinFactor);
    h2->Rebin(rebinFactor);
    h3->Rebin(rebinFactor);
    h4->Rebin(rebinFactor);

    h1->SetLineColorAlpha(kWhite, 1.);
    h1->SetTitle("");
    h1->GetXaxis()->SetTitle("Offline p_{T} [GeV]");
    h1->GetXaxis()->SetTitleSize(0.045);
    h1->GetXaxis()->SetTitleOffset(1.1);
    h1->GetYaxis()->SetTitle("Efficiency");
    h1->GetYaxis()->SetTitleSize(0.045);
    h1->GetYaxis()->SetTitleOffset(1.1);
    h1->GetYaxis()->SetRangeUser(0.,1.5);
    h1->Draw();

    c1->Update();
    c1->RedrawAxis();
    TLine l;
    l.DrawLine(c1->GetUxmin(), c1->GetUymax(), c1->GetUxmax(), c1->GetUymax());
    l.DrawLine(c1->GetUxmax(), c1->GetUymin(), c1->GetUxmax(), c1->GetUymax());

    TEfficiency* pEff1 = 0;

    if(TEfficiency::CheckConsistency(*h2,*h1)){
      pEff1 = new TEfficiency(*h2,*h1);
      pEff1->SetLineWidth(3.);
      pEff1->SetLineColor(kBlack);
      pEff1->Draw("same");
    }

    // Overlay the efficiency for seedpt
    TEfficiency* pEff2 = 0;

    if(TEfficiency::CheckConsistency(*h4,*h3)){
      pEff2 = new TEfficiency(*h4,*h3);
      pEff2->SetLineWidth(3.);
      pEff2->SetLineColor(kRed); // Use a different color for distinction
      pEff2->Draw("same");
    }

    TLegend *legend1 = new TLegend(0.15, 0.65, 0.35, 0.85);
    legend1->SetTextFont(42);
    legend1->SetLineColor(0);
    legend1->SetTextSize(0.045);
    legend1->SetFillColor(0);
    legend1->AddEntry(pEff1, "L1 jet p_{T} > 100 GeV", "l");
    legend1->AddEntry(pEff2, "Seed p_{T} > 100 GeV", "l"); // Adjust the legend entry as needed
    legend1->Draw("same");
}
