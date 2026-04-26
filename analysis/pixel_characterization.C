// pixel_characterization.C
//
// Caracterización del píxel reconstruido (iteración 0.7).
// Tres paneles:
//   1. Mapa de frecuencia de píxeles virtuales (i_X, j_Y) 16×16.
//   2. Correlación de topologías (code_X, code_Y) 5×5.
//   3. Distribución del número total de barras encendidas por evento.
//
// Predicciones:
//   Panel 1: cobertura ~uniforme de los 256 píxeles.
//   Panel 2: correlación X–Y baja (χ² de independencia).
//   Panel 3: pico en 4 (overlap×overlap), cola en 2–3 y hacia arriba.
//
// Uso desde build/:
//   root -l '../analysis/pixel_characterization.C("xy_scan.root")'

#include <vector>
#include <cmath>
#include <numeric>

static double bar_center_x(int b) {
    if (b <  8) return -14.0 + 4.0 * b;
    if (b < 16) return -12.0 + 4.0 * (b - 8);
    return 0.;
}
static double bar_center_y(int b) {
    if (b >= 16 && b < 24) return -14.0 + 4.0 * (b - 16);
    if (b >= 24 && b < 32) return -12.0 + 4.0 * (b - 24);
    return 0.;
}

// Devuelve (código topología, índice de píxel virtual 0..15) en un eje.
// code: 0=no dispara, 1=sup-only, 2=inf-only, 3=overlap, 4=delta-ray
// pixel: índice del overlap (0..15), −1 si no aplica.
struct AxisReco { int code; int pixel; double pos; };

static AxisReco reco_axis_X(const Double_t edep[32], double thr) {
    AxisReco r{0, -1, NAN};
    int bs = -1, bi = -1;
    double ms = thr, mi = thr;
    for (int b = 0; b <  8; ++b) if (edep[b] > ms) { ms = edep[b]; bs = b; }
    for (int b = 8; b < 16; ++b) if (edep[b] > mi) { mi = edep[b]; bi = b; }

    if (bs < 0 && bi < 0) return r;
    if (bs >= 0 && bi < 0) { r.code=1; r.pos=bar_center_x(bs); return r; }
    if (bs <  0 && bi >= 0) { r.code=2; r.pos=bar_center_x(bi); return r; }

    double cs = bar_center_x(bs), ci = bar_center_x(bi);
    double left = std::max(cs-1.5, ci-1.5), right = std::min(cs+1.5, ci+1.5);
    if (left > right) { r.code=4; r.pos=(ms>mi)?cs:ci; return r; }

    r.code  = 3;
    r.pos   = 0.5*(left+right);
    // Píxel virtual = índice del overlap (bs×2 + desplazamiento relativo)
    // Hay 16 pares (bs, bi) válidos: bi_local = bi-8 ∈ {0..7}, bs ∈ {0..7}.
    // Los pares con overlap son bs y bs+0 o bs-1 de X-inf.
    // Enumeramos: para cada bs (0..7) hay dos pares (bi=bs, diff=+2)
    // y (bi=bs-1, diff=-2). Asignamos índice i_pix = 2*bs + (bi==bs?0:1)
    // con saturación en los bordes.
    int bi_local = bi - 8;
    r.pixel = 2 * bs + (bi_local >= bs ? 0 : 1);
    if (r.pixel < 0)  r.pixel = 0;
    if (r.pixel > 15) r.pixel = 15;
    return r;
}

static AxisReco reco_axis_Y(const Double_t edep[32], double thr) {
    AxisReco r{0, -1, NAN};
    int bs = -1, bi = -1;
    double ms = thr, mi = thr;
    for (int b = 16; b < 24; ++b) if (edep[b] > ms) { ms = edep[b]; bs = b; }
    for (int b = 24; b < 32; ++b) if (edep[b] > mi) { mi = edep[b]; bi = b; }

    if (bs < 0 && bi < 0) return r;
    if (bs >= 0 && bi < 0) { r.code=1; r.pos=bar_center_y(bs); return r; }
    if (bs <  0 && bi >= 0) { r.code=2; r.pos=bar_center_y(bi); return r; }

    double cs = bar_center_y(bs), ci = bar_center_y(bi);
    double left = std::max(cs-1.5, ci-1.5), right = std::min(cs+1.5, ci+1.5);
    if (left > right) { r.code=4; r.pos=(ms>mi)?cs:ci; return r; }

    r.code = 3;
    r.pos  = 0.5*(left+right);
    int bs_local = bs - 16, bi_local = bi - 24;
    r.pixel = 2 * bs_local + (bi_local >= bs_local ? 0 : 1);
    if (r.pixel < 0)  r.pixel = 0;
    if (r.pixel > 15) r.pixel = 15;
    return r;
}

// ---------------------------------------------------------------------------
void pixel_characterization(const char* fname = "xy_scan.root",
                             double thresh_MeV = 0.05)
{
    TFile* f = TFile::Open(fname);
    if (!f || f->IsZombie()) { Printf("[ERROR] %s", fname); return; }
    TTree* t = (TTree*)f->Get("hodo");
    if (!t) { Printf("[ERROR] TTree 'hodo' no encontrado"); return; }

    auto* h_pixel   = new TH2I("h_pixel",   "Frecuencia de p#acute{i}xeles virtuales;"
                                             "i_{X} (p#acute{i}xel X);j_{Y} (p#acute{i}xel Y)",
                                16, -0.5, 15.5, 16, -0.5, 15.5);
    auto* h_topo    = new TH2I("h_topo",    "Correlaci#acute{o}n de topolog#acute{i}as;"
                                             "code_{X};code_{Y}",
                                5, -0.5, 4.5, 5, -0.5, 4.5);
    auto* h_nbars   = new TH1I("h_nbars",   "Barras encendidas por evento;"
                                             "N_{barras} (X+Y, edep > thr);Eventos",
                                20, -0.5, 19.5);

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
    Printf("Leyendo %lld eventos ...", nev);

    for (Long64_t ev = 0; ev < nev; ++ev) {
        t->GetEntry(ev);

        auto rx = reco_axis_X(edep, thresh_MeV);
        auto ry = reco_axis_Y(edep, thresh_MeV);

        if (rx.code == 3 && ry.code == 3)
            h_pixel->Fill(rx.pixel, ry.pixel);

        h_topo->Fill(rx.code, ry.code);

        int nbars = 0;
        for (int b = 0; b < 32; ++b) if (edep[b] > thresh_MeV) ++nbars;
        h_nbars->Fill(nbars);
    }

    // Estadística correlación topológica: coeficiente de Cramér's V
    // (mide asociación entre variables categóricas; V=0: independientes)
    double chi2 = 0.;
    double N    = (double)nev;
    double row_sum[5] = {}, col_sum[5] = {};
    for (int cx = 0; cx < 5; ++cx)
        for (int cy = 0; cy < 5; ++cy) {
            row_sum[cx] += h_topo->GetBinContent(cx+1, cy+1);
            col_sum[cy] += h_topo->GetBinContent(cx+1, cy+1);
        }
    for (int cx = 0; cx < 5; ++cx)
        for (int cy = 0; cy < 5; ++cy) {
            double obs = h_topo->GetBinContent(cx+1, cy+1);
            double exp_ = row_sum[cx] * col_sum[cy] / N;
            if (exp_ > 0) chi2 += (obs-exp_)*(obs-exp_)/exp_;
        }
    int k = 5;  // categories
    double cramers_V = std::sqrt(chi2 / (N * (k-1)));
    Printf("Correlación topológica X–Y: Cramér's V = %.4f  (0=independiente, 1=máxima)", cramers_V);
    Printf("  Predicción: V < 0.05 (física ortogonal en X e Y)");

    // Cobertura de píxeles virtuales (overlap×overlap)
    int pix_fired = 0;
    long pix_min = LONG_MAX, pix_max = 0;
    for (int ix = 1; ix <= 16; ++ix)
        for (int iy = 1; iy <= 16; ++iy) {
            long cnt = h_pixel->GetBinContent(ix, iy);
            if (cnt > 0) ++pix_fired;
            if (cnt < pix_min) pix_min = cnt;
            if (cnt > pix_max) pix_max = cnt;
        }
    Printf("Píxeles virtuales activados: %d / 256  (min=%ld  max=%ld)", pix_fired, pix_min, pix_max);

    // --------------- Canvas 1×3 ------------------------------------------------
    gStyle->SetOptStat(0);
    gStyle->SetPalette(kBird);

    TCanvas* c = new TCanvas("pixel_char", "Caracterización de píxel", 1800, 560);
    c->Divide(3, 1);

    c->cd(1);
    gPad->SetRightMargin(0.15); gPad->SetLeftMargin(0.12);
    h_pixel->SetContour(64);
    h_pixel->Draw("COLZ");

    c->cd(2);
    gPad->SetRightMargin(0.15); gPad->SetLeftMargin(0.12);
    // Etiquetas de los ejes (códigos 0-4)
    const char* labels[5] = {"ninguna","X-sup","X-inf","overlap","#delta-ray"};
    for (int i = 0; i < 5; ++i) {
        h_topo->GetXaxis()->SetBinLabel(i+1, labels[i]);
        h_topo->GetYaxis()->SetBinLabel(i+1, labels[i]);
    }
    h_topo->SetContour(64);
    h_topo->Draw("COLZ TEXT");

    TLatex* ltx = new TLatex();
    ltx->SetNDC(); ltx->SetTextSize(0.038);
    ltx->DrawLatex(0.18, 0.88, Form("Cram#acute{e}r's V = %.4f", cramers_V));

    c->cd(3);
    gPad->SetRightMargin(0.05); gPad->SetLeftMargin(0.14);
    h_nbars->SetFillColor(kAzure+2);
    h_nbars->SetLineColor(kBlue+2);
    h_nbars->Draw("HIST");
    // Línea en 4 (esperado overlap×overlap)
    auto* ln = new TLine(4, 0, 4, h_nbars->GetMaximum()*0.9);
    ln->SetLineColor(kRed+1); ln->SetLineStyle(2); ln->SetLineWidth(2);
    ln->Draw("SAME");
    TLatex ltx2; ltx2.SetNDC(); ltx2.SetTextSize(0.036);
    ltx2.DrawLatex(0.55, 0.82, "moda esperada = 4");

    c->SaveAs("pixel_characterization.png");
    Printf("Figura guardada: pixel_characterization.png");

    f->Close();
}
