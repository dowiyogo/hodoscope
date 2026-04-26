// xy_uniformity.C
//
// Análisis de uniformidad 2D del hodoscopio único (iteración 0.7).
// Produce tres mapas 2D:
//   1. Edep total medio por celda (x_true, y_true).
//   2. Eficiencia geométrica: P(hit en X AND hit en Y | threshold).
//   3. Número promedio de barras encendidas (plano X y Y separados).
//
// Uso desde build/:
//   root -l '../analysis/xy_uniformity.C("xy_scan.root")'

#include <vector>
#include <string>
#include <cmath>

// ---------------------------------------------------------------------------
// Centros de barras (idéntico a d_scan_analysis.C).
//   bar 0..7:   X-sup → −14, −10, −6, −2, +2, +6, +10, +14 mm
//   bar 8..15:  X-inf, offset +2 mm → −12, −8, −4, 0, +4, +8, +12, +16 mm
//   bar 16..23: Y-sup → mismo patrón en Y (offset 0)
//   bar 24..31: Y-inf, offset +2 mm en Y
// ---------------------------------------------------------------------------
static double bar_center_x(int b) {
    if (b <  8) return -14.0 + 4.0 * b;
    if (b < 16) return -12.0 + 4.0 * (b - 8);
    return 0.;  // no aplica para barras Y
}

static double bar_center_y(int b) {
    if (b >= 16 && b < 24) return -14.0 + 4.0 * (b - 16);
    if (b >= 24 && b < 32) return -12.0 + 4.0 * (b - 24);
    return 0.;  // no aplica para barras X
}

struct RecoXY { double x; double y; int code_x; int code_y; };

static RecoXY reco_xy(const Double_t edep[32], double thr) {
    RecoXY r{NAN, NAN, 0, 0};
    // --- Plano X ---
    int bx_sup = -1, bx_inf = -1;
    double mx_s = thr, mx_i = thr;
    for (int b = 0; b < 8;  ++b) if (edep[b] > mx_s) { mx_s = edep[b]; bx_sup = b; }
    for (int b = 8; b < 16; ++b) if (edep[b] > mx_i) { mx_i = edep[b]; bx_inf = b; }

    if (bx_sup >= 0 && bx_inf >= 0) {
        double cs = bar_center_x(bx_sup), ci = bar_center_x(bx_inf);
        double left = std::max(cs - 1.5, ci - 1.5), right = std::min(cs + 1.5, ci + 1.5);
        if (left <= right) { r.x = 0.5*(left+right); r.code_x = 3; }
        else               { r.x = (mx_s>mx_i)?cs:ci; r.code_x = 4; }
    } else if (bx_sup >= 0) { r.x = bar_center_x(bx_sup); r.code_x = 1; }
    else if (bx_inf >= 0)   { r.x = bar_center_x(bx_inf); r.code_x = 2; }

    // --- Plano Y ---
    int by_sup = -1, by_inf = -1;
    double my_s = thr, my_i = thr;
    for (int b = 16; b < 24; ++b) if (edep[b] > my_s) { my_s = edep[b]; by_sup = b; }
    for (int b = 24; b < 32; ++b) if (edep[b] > my_i) { my_i = edep[b]; by_inf = b; }

    if (by_sup >= 0 && by_inf >= 0) {
        double cs = bar_center_y(by_sup), ci = bar_center_y(by_inf);
        double left = std::max(cs - 1.5, ci - 1.5), right = std::min(cs + 1.5, ci + 1.5);
        if (left <= right) { r.y = 0.5*(left+right); r.code_y = 3; }
        else               { r.y = (my_s>my_i)?cs:ci; r.code_y = 4; }
    } else if (by_sup >= 0) { r.y = bar_center_y(by_sup); r.code_y = 1; }
    else if (by_inf >= 0)   { r.y = bar_center_y(by_inf); r.code_y = 2; }

    return r;
}

// ---------------------------------------------------------------------------
void xy_uniformity(const char* fname = "xy_scan.root",
                   double thresh_MeV = 0.05,
                   double dxy        = 1.0)
{
    TFile* f = TFile::Open(fname);
    if (!f || f->IsZombie()) { Printf("[ERROR] No se puede abrir %s", fname); return; }

    TTree* t = (TTree*)f->Get("hodo");
    if (!t) { Printf("[ERROR] TTree 'hodo' no encontrado"); return; }

    // --- Rango de la grilla (−15..+15 con paso dxy=1mm → 31 bins) ---
    const double xylo = -15.5, xyhi = 15.5;
    const int    nbin = (int)std::round((xyhi - xylo) / dxy);

    // Mapas 2D acumuladores
    auto* h_edep_sum  = new TH2D("h_edep_sum",  "", nbin, xylo, xyhi, nbin, xylo, xyhi);
    auto* h_count     = new TH2D("h_count",      "", nbin, xylo, xyhi, nbin, xylo, xyhi);
    auto* h_eff       = new TH2D("h_eff",        "", nbin, xylo, xyhi, nbin, xylo, xyhi);
    auto* h_nbars_x   = new TH2D("h_nbars_x",    "", nbin, xylo, xyhi, nbin, xylo, xyhi);
    auto* h_nbars_y   = new TH2D("h_nbars_y",    "", nbin, xylo, xyhi, nbin, xylo, xyhi);
    for (auto* h : {h_edep_sum,h_count,h_eff,h_nbars_x,h_nbars_y}) h->Sumw2(false);

    // Lectura del TTree
    Double_t prim_x, prim_y;
    Double_t edep[32];
    t->SetBranchAddress("prim_x", &prim_x);
    t->SetBranchAddress("prim_y", &prim_y);
    char bname[16];
    for (int i = 0; i < 32; ++i) {
        snprintf(bname, sizeof(bname), "edep_%02d", i);
        t->SetBranchAddress(bname, &edep[i]);
    }

    Long64_t nev = t->GetEntries();
    Printf("Leyendo %lld eventos de %s ...", nev, fname);

    for (Long64_t ev = 0; ev < nev; ++ev) {
        t->GetEntry(ev);

        // Edep total en las 32 barras
        double edep_tot = 0.;
        for (int i = 0; i < 32; ++i) edep_tot += edep[i];

        // Barras encendidas en cada plano
        int nx_fire = 0, ny_fire = 0;
        for (int b = 0;  b < 16; ++b) if (edep[b] > thresh_MeV) ++nx_fire;
        for (int b = 16; b < 32; ++b) if (edep[b] > thresh_MeV) ++ny_fire;

        // Reconstrucción X e Y
        auto reco = reco_xy(edep, thresh_MeV);
        int hit_X = (reco.code_x > 0) ? 1 : 0;
        int hit_Y = (reco.code_y > 0) ? 1 : 0;

        h_edep_sum ->Fill(prim_x, prim_y, edep_tot);
        h_count    ->Fill(prim_x, prim_y, 1.);
        h_eff      ->Fill(prim_x, prim_y, (double)(hit_X && hit_Y));
        h_nbars_x  ->Fill(prim_x, prim_y, (double)nx_fire);
        h_nbars_y  ->Fill(prim_x, prim_y, (double)ny_fire);
    }

    // Normalizar por número de eventos por celda
    auto* h_edep_mean  = (TH2D*)h_edep_sum->Clone("h_edep_mean");
    auto* h_eff_mean   = (TH2D*)h_eff     ->Clone("h_eff_mean");
    auto* h_nbarsx_mean= (TH2D*)h_nbars_x ->Clone("h_nbarsx_mean");
    auto* h_nbarsy_mean= (TH2D*)h_nbars_y ->Clone("h_nbarsy_mean");
    h_edep_mean  ->Divide(h_count);
    h_eff_mean   ->Divide(h_count);
    h_nbarsx_mean->Divide(h_count);
    h_nbarsy_mean->Divide(h_count);

    // Estadísticas zona central (|x|<13, |y|<13)
    double edep_sum_c = 0., edep_sq_c = 0.; int ncells = 0;
    double eff_sum_c  = 0.;
    for (int ix = 1; ix <= nbin; ++ix) {
        for (int iy = 1; iy <= nbin; ++iy) {
            double xc = h_edep_mean->GetXaxis()->GetBinCenter(ix);
            double yc = h_edep_mean->GetYaxis()->GetBinCenter(iy);
            if (std::abs(xc) > 13. || std::abs(yc) > 13.) continue;
            double e = h_edep_mean->GetBinContent(ix,iy);
            double ef = h_eff_mean->GetBinContent(ix,iy);
            edep_sum_c += e; edep_sq_c += e*e; eff_sum_c += ef; ++ncells;
        }
    }
    double edep_mean_c = edep_sum_c / ncells;
    double edep_rms_c  = std::sqrt(edep_sq_c/ncells - edep_mean_c*edep_mean_c);
    double eff_mean_c  = eff_sum_c / ncells;
    Printf("Zona central (|x|,|y|<13mm): %d celdas", ncells);
    Printf("  <edep_total> = %.4f MeV   rms/mean = %.1f%%",
           edep_mean_c, 100.*edep_rms_c/edep_mean_c);
    Printf("  <eficiencia> = %.4f", eff_mean_c);

    // --------------- Canvas 1×3: mapas de uniformidad -----------------------
    gStyle->SetOptStat(0);
    gStyle->SetPalette(kBird);

    TCanvas* c1 = new TCanvas("uniformity_maps", "Uniformidad 2D", 1800, 560);
    c1->Divide(3, 1);

    auto styleH2 = [](TH2D* h, const char* ztitle) {
        h->GetXaxis()->SetTitle("x_{true} [mm]");
        h->GetYaxis()->SetTitle("y_{true} [mm]");
        h->GetZaxis()->SetTitle(ztitle);
        h->GetXaxis()->SetTitleSize(0.05);
        h->GetYaxis()->SetTitleSize(0.05);
        h->GetZaxis()->SetTitleSize(0.045);
        h->GetZaxis()->SetTitleOffset(1.2);
        h->SetContour(64);
    };

    c1->cd(1);
    gPad->SetRightMargin(0.15); gPad->SetLeftMargin(0.12);
    h_edep_mean->SetTitle("#LTedep_{total}#GT por celda;x_{true} [mm];y_{true} [mm]");
    styleH2(h_edep_mean, "#LTedep#GT [MeV]");
    h_edep_mean->Draw("COLZ");

    c1->cd(2);
    gPad->SetRightMargin(0.15); gPad->SetLeftMargin(0.12);
    h_eff_mean->SetTitle("Eficiencia geom#acute{e}trica;x_{true} [mm];y_{true} [mm]");
    styleH2(h_eff_mean, "P(hit_{X} AND hit_{Y})");
    h_eff_mean->GetZaxis()->SetRangeUser(0., 1.05);
    h_eff_mean->Draw("COLZ");

    c1->cd(3);
    gPad->SetRightMargin(0.15); gPad->SetLeftMargin(0.12);
    h_nbarsx_mean->SetTitle("#LTbarras encendidas#GT plano X;x_{true} [mm];y_{true} [mm]");
    styleH2(h_nbarsx_mean, "#LTN_{barras,X}#GT");
    h_nbarsx_mean->Draw("COLZ");

    c1->SaveAs("uniformity_maps.png");
    Printf("Figura guardada: uniformity_maps.png");

    f->Close();
}
