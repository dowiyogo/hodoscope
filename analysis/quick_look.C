// quick_look.C
//
// Inspección mínima del TTree producido por hodoscope.
//
// Uso:
//   root -l 'quick_look.C("hodoscope.root")'
//
// Hace tres cosas:
//   1) Cuenta eventos.
//   2) Para cada barra: imprime el promedio de energía depositada y el
//      número de eventos con edep > 0.
//   3) Construye un mapa 2D px-py reconstruido (histograma de píxeles
//      coincidentes) usando el criterio "barra con mayor edep" en cada
//      subplano.
//
// Diseño consciente: no asumimos thresholds ni walk-time corrections;
// esto es sólo un sanity check de la salida.

void quick_look(const char* fname = "hodoscope.root")
{
  TFile* f = TFile::Open(fname, "READ");
  if (!f || f->IsZombie()) { Printf("No puedo abrir %s", fname); return; }

  TTree* t = (TTree*)f->Get("hodo");
  if (!t) { Printf("No hay TTree 'hodo' en %s", fname); return; }

  const Long64_t N = t->GetEntries();
  Printf("Eventos totales: %lld", N);

  // ----- bind branches ----------------------------------------------------
  Int_t    eventID;
  Double_t prim_x, prim_y, prim_z, prim_px, prim_py, prim_pz, prim_E;
  Double_t edep[32];
  Int_t    nph[32];

  t->SetBranchAddress("eventID", &eventID);
  t->SetBranchAddress("prim_x",  &prim_x);
  t->SetBranchAddress("prim_y",  &prim_y);
  t->SetBranchAddress("prim_z",  &prim_z);
  t->SetBranchAddress("prim_px", &prim_px);
  t->SetBranchAddress("prim_py", &prim_py);
  t->SetBranchAddress("prim_pz", &prim_pz);
  t->SetBranchAddress("prim_E",  &prim_E);

  for (int i = 0; i < 32; ++i) {
    char b[16];
    snprintf(b, 16, "edep_%02d", i); t->SetBranchAddress(b, &edep[i]);
    snprintf(b, 16, "nph_%02d",  i); t->SetBranchAddress(b, &nph[i]);
  }

  // ----- estadísticas por barra -------------------------------------------
  Double_t sum_edep[32]    = {0};
  Long64_t hits_count[32]  = {0};

  // ----- mapa píxel reconstruido (16x16) ----------------------------------
  // i_X (barra X de máximo edep entre 0..15): pero la indexación física
  // i_X ∈ [0..15] proviene de combinar X_sup (0..7) y X_inf (8..15) según
  // el offset. Para esta vista simplificada usamos:
  //   i_X = arg max edep[0..15]  (sin distinguir sup/inf — sólo "qué barra")
  //   j_Y = arg max edep[16..31] - 16
  TH2I* hPix = new TH2I("hPix", "Pixel reconstruido (max edep);i_X (0-15);j_Y (0-15)",
                       16, -0.5, 15.5, 16, -0.5, 15.5);

  // ----- main loop --------------------------------------------------------
  for (Long64_t ev = 0; ev < N; ++ev) {
    t->GetEntry(ev);
    int iX = -1; double maxX = 0.;
    int iY = -1; double maxY = 0.;
    for (int i = 0; i < 32; ++i) {
      sum_edep[i] += edep[i];
      if (edep[i] > 0.) ++hits_count[i];
      if (i < 16) {
        if (edep[i] > maxX) { maxX = edep[i]; iX = i; }
      } else {
        if (edep[i] > maxY) { maxY = edep[i]; iY = i - 16; }
      }
    }
    if (iX >= 0 && iY >= 0) hPix->Fill(iX, iY);
  }

  // ----- imprimir tabla ---------------------------------------------------
  Printf("\nBarra | <edep> [keV] | hits | tipo");
  Printf("------+--------------+------+--------------");
  const char* labels[4] = {"X_sup", "X_inf", "Y_sup", "Y_inf"};
  for (int i = 0; i < 32; ++i) {
    double mean_keV = (N > 0) ? 1000. * sum_edep[i] / N : 0.;
    Printf(" %3d  | %12.2f | %4lld | %s",
           i, mean_keV, hits_count[i], labels[i/8]);
  }

  // ----- canvas resultado -------------------------------------------------
  TCanvas* c = new TCanvas("c", "hodoscope quick look", 1200, 500);
  c->Divide(2, 1);

  c->cd(1);
  hPix->SetStats(0);
  hPix->Draw("COLZ");

  c->cd(2);
  TH1D* hEdepX = new TH1D("hEdepX","Edep total plano X;edep [MeV];eventos",
                          100, 0., 2.);
  TH1D* hEdepY = new TH1D("hEdepY","Edep total plano Y;edep [MeV];eventos",
                          100, 0., 2.);
  for (Long64_t ev = 0; ev < N; ++ev) {
    t->GetEntry(ev);
    double ex = 0., ey = 0.;
    for (int i = 0;  i < 16; ++i) ex += edep[i];
    for (int i = 16; i < 32; ++i) ey += edep[i];
    hEdepX->Fill(ex);
    hEdepY->Fill(ey);
  }
  hEdepX->SetLineColor(kBlue+1);
  hEdepY->SetLineColor(kRed+1);
  hEdepX->Draw();
  hEdepY->Draw("SAME");

  TLegend* leg = new TLegend(0.6, 0.7, 0.88, 0.88);
  leg->AddEntry(hEdepX, "Plano X (sum 0-15)", "l");
  leg->AddEntry(hEdepY, "Plano Y (sum 16-31)", "l");
  leg->Draw();

  c->SaveAs("quick_look.png");
  Printf("\nFigura escrita: quick_look.png");
}
