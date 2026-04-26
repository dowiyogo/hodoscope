// x_resolution.C
//
// Análisis del escaneo posicional 1D en X (input: salida de x_scan.mac).
//
// Demuestra el "truco del offset" entre X-sup y X-inf:
//   - 8 barras por subplano de 3 mm + 1 mm gap = pitch 4 mm.
//   - Subplano inferior desplazado +2 mm respecto al superior.
//   - Cada 1 mm de x_true mapea a un patrón único de barras encendidas
//     (16 "píxeles virtuales" de 1 mm en lugar de 8 píxeles físicos
//     de 3 mm).
//
// Predicción analítica:
//   - Residual x_reco - x_true uniforme en [-0.5, +0.5] mm.
//   - RMS = 1/√12 ≈ 0.289 mm.
//
// Genera 3 figuras:
//   1) edep_vs_x.png    : <edep> de cada barra X vs x_true (16 curvas).
//   2) p_fires_vs_x.png : P(barra dispara) vs x_true.
//   3) residual.png     : x_reco - x_true vs x_true (diente de sierra).
//
// Uso:
//   root -l 'x_resolution.C("hodoscope.root")'
//   root -l 'x_resolution.C("hodoscope.root", 0.05)'   // threshold custom

#include <vector>
#include <utility>
#include <cmath>


//-----------------------------------------------------------------------
// Centros de las barras X (en mm).
//   bar 0..7:  X-sup, sin offset      → -14, -10, -6, -2, +2, +6, +10, +14
//   bar 8..15: X-inf, offset +2 mm    → -12,  -8, -4,  0, +4, +8, +12, +16
//-----------------------------------------------------------------------
double bar_center_x(int bar_idx) {
  if (bar_idx < 8) return -14.0 + 4.0 * bar_idx;
  else             return -12.0 + 4.0 * (bar_idx - 8);
}

//-----------------------------------------------------------------------
// Reconstrucción combinatoria de x usando la barra de máximo edep en
// cada subplano. Devuelve x_reco y un código de topología:
//   0 = ninguna barra dispara
//   1 = sólo X-sup
//   2 = sólo X-inf
//   3 = ambos planos disparan (overlap)
//   4 = ambos pero barras no contiguas (δ-ray contamination)
//-----------------------------------------------------------------------
struct RecoResult { double x; int code; int b_sup; int b_inf; };

RecoResult reco_x_two_planes(const Double_t edep[32], double thresh_MeV) {
  int b_sup = -1, b_inf = -1;
  double max_sup = thresh_MeV, max_inf = thresh_MeV;
  for (int b = 0; b < 8;  ++b) if (edep[b] > max_sup) { max_sup = edep[b]; b_sup = b; }
  for (int b = 8; b < 16; ++b) if (edep[b] > max_inf) { max_inf = edep[b]; b_inf = b; }

  RecoResult r{NAN, 0, b_sup, b_inf};
  if (b_sup < 0 && b_inf < 0)              { r.code = 0; return r; }
  if (b_sup >= 0 && b_inf < 0)             { r.x = bar_center_x(b_sup); r.code = 1; return r; }
  if (b_sup <  0 && b_inf >= 0)            { r.x = bar_center_x(b_inf); r.code = 2; return r; }

  // Ambos: intersección de las dos barras (cada una de 3 mm de ancho).
  double c_sup = bar_center_x(b_sup);
  double c_inf = bar_center_x(b_inf);
  double left  = std::max(c_sup - 1.5, c_inf - 1.5);
  double right = std::min(c_sup + 1.5, c_inf + 1.5);
  if (left > right) {
    // No hay intersección: barras lejanas → δ-ray. Caemos al de más edep.
    r.x = (max_sup > max_inf) ? c_sup : c_inf;
    r.code = 4; return r;
  }
  r.x = 0.5 * (left + right);
  r.code = 3;
  return r;
}

//-----------------------------------------------------------------------
void x_resolution(const char* fname = "hodoscope.root",
                  double edep_threshold_MeV = 0.05)
{
  TFile* f = TFile::Open(fname, "READ");
  if (!f || f->IsZombie()) { Printf("[ERROR] No puedo abrir %s", fname); return; }

  TTree* t = (TTree*)f->Get("hodo");
  if (!t) { Printf("[ERROR] No hay TTree 'hodo' en %s", fname); return; }

  Double_t prim_x, edep[32];
  t->SetBranchAddress("prim_x", &prim_x);
  for (int i = 0; i < 16; ++i) {
    char b[16]; snprintf(b, 16, "edep_%02d", i);
    t->SetBranchAddress(b, &edep[i]);
  }

  const Long64_t N = t->GetEntries();
  Printf("Eventos totales:   %lld", N);
  Printf("Threshold:         %.0f keV", edep_threshold_MeV * 1000);

  // Rango del scan (un poco más amplio que el escaneo nominal para ver bordes)
  const double xmin = -7.0, xmax = +7.0;
  const int    nbins = 140;   // 0.1 mm per bin

  // ----- histos -----------------------------------------------------------
  std::vector<TProfile*> hEdep(16), hFire(16);
  for (int b = 0; b < 16; ++b) {
    hEdep[b] = new TProfile(Form("hEdep_%02d", b),
                             ";x_{true} [mm];#LTedep#GT [MeV]",
                             nbins, xmin, xmax);
    hFire[b] = new TProfile(Form("hFire_%02d", b),
                             ";x_{true} [mm];P(fires)",
                             nbins, xmin, xmax);
  }

  TH2D* hResid = new TH2D("hResid",
      ";x_{true} [mm];x_{reco} - x_{true} [mm]",
      nbins, xmin, xmax,
      120, -3., +3.);

  // Histos por código de topología
  TH1D* hResidOverlap = new TH1D("hResidOverlap",
      "Topología 3: ambos planos (overlap);x_{reco} - x_{true} [mm];eventos",
      80, -2., +2.);
  TH1D* hResidSingle  = new TH1D("hResidSingle",
      "Topologías 1+2: un solo plano;x_{reco} - x_{true} [mm];eventos",
      80, -2., +2.);
  TH1D* hCode = new TH1D("hCode",
      "Distribución de topologías;código;eventos",
      5, -0.5, 4.5);

  // ----- main loop --------------------------------------------------------
  for (Long64_t ev = 0; ev < N; ++ev) {
    t->GetEntry(ev);
    if (prim_x < xmin || prim_x > xmax) continue;

    for (int b = 0; b < 16; ++b) {
      hEdep[b]->Fill(prim_x, edep[b]);
      hFire[b]->Fill(prim_x, (edep[b] > edep_threshold_MeV) ? 1.0 : 0.0);
    }

    auto r = reco_x_two_planes(edep, edep_threshold_MeV);
    hCode->Fill(r.code);
    if (r.code > 0) {
      double resid = r.x - prim_x;
      hResid->Fill(prim_x, resid);
      if      (r.code == 3) hResidOverlap->Fill(resid);
      else if (r.code == 1 || r.code == 2) hResidSingle->Fill(resid);
    }
  }

  Printf("\nDistribución de topologías:");
  Printf("  0 (no fire)        : %.0f", hCode->GetBinContent(1));
  Printf("  1 (sólo X-sup)     : %.0f", hCode->GetBinContent(2));
  Printf("  2 (sólo X-inf)     : %.0f", hCode->GetBinContent(3));
  Printf("  3 (overlap)        : %.0f", hCode->GetBinContent(4));
  Printf("  4 (δ-ray noise)    : %.0f", hCode->GetBinContent(5));

  Printf("\nResolución (RMS del residual):");
  Printf("  Overlap (codigo 3) : %.3f mm   [predicción analítica: 0.289 mm]",
         hResidOverlap->GetRMS());
  Printf("  Single  (codigos 1+2): %.3f mm", hResidSingle->GetRMS());

  // ----- canvas 1: edep medio por barra ----------------------------------
  TCanvas* c1 = new TCanvas("c1", "edep per bar vs x", 1200, 600);
  int colors[16] = {kBlue+1, kRed+1, kGreen+2, kMagenta+1, kOrange+7, kCyan+2,
                    kPink+10, kViolet+1, kAzure+1, kSpring-6, kYellow+3,
                    kTeal+3, kBlue-7, kRed-7, kGreen-7, kMagenta-7};
  hEdep[0]->SetTitle("#LTedep#GT por barra X vs x_{true};x_{true} [mm];#LTedep#GT [MeV]");
  hEdep[0]->SetMaximum(0.30);
  hEdep[0]->SetMinimum(0.0);
  for (int b = 0; b < 16; ++b) {
    hEdep[b]->SetLineColor(colors[b]);
    hEdep[b]->SetLineWidth(2);
    if (b < 8) hEdep[b]->SetLineStyle(1);  // X-sup sólido
    else       hEdep[b]->SetLineStyle(2);  // X-inf punteado
    hEdep[b]->Draw(b == 0 ? "" : "SAME");
  }
  c1->SaveAs("edep_vs_x.png");

  // ----- canvas 2: P(fires) por barra ------------------------------------
  TCanvas* c2 = new TCanvas("c2", "P(fires) per bar vs x", 1200, 600);
  hFire[0]->SetTitle(Form("P(edep > %.0f keV) por barra X vs x_{true};x_{true} [mm];P",
                           edep_threshold_MeV*1000));
  hFire[0]->SetMaximum(1.15);
  hFire[0]->SetMinimum(0.0);
  for (int b = 0; b < 16; ++b) {
    hFire[b]->SetLineColor(colors[b]);
    hFire[b]->SetLineWidth(2);
    hFire[b]->SetLineStyle(b < 8 ? 1 : 2);
    hFire[b]->Draw(b == 0 ? "" : "SAME");
  }
  c2->SaveAs("p_fires_vs_x.png");

  // ----- canvas 3: residual ----------------------------------------------
  TCanvas* c3 = new TCanvas("c3", "residual", 1400, 500);
  c3->Divide(3, 1);

  c3->cd(1);
  hResid->SetTitle("Residual vs x_{true} (diente de sierra);x_{true} [mm];x_{reco} - x_{true} [mm]");
  hResid->Draw("COLZ");

  c3->cd(2);
  hResidOverlap->SetLineColor(kBlue+1);
  hResidOverlap->SetLineWidth(2);
  hResidOverlap->Draw();
  TLatex tx;
  tx.SetNDC(); tx.SetTextSize(0.04);
  tx.DrawLatex(0.18, 0.85, Form("RMS = %.3f mm", hResidOverlap->GetRMS()));
  tx.DrawLatex(0.18, 0.80, "(esperado: 0.289 mm)");

  c3->cd(3);
  hResidSingle->SetLineColor(kRed+1);
  hResidSingle->SetLineWidth(2);
  hResidSingle->Draw();
  tx.DrawLatex(0.18, 0.85, Form("RMS = %.3f mm", hResidSingle->GetRMS()));

  c3->SaveAs("residual.png");

  Printf("\nFiguras: edep_vs_x.png, p_fires_vs_x.png, residual.png");
}
