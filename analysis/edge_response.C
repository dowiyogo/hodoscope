// edge_response.C
//
// Análisis de respuesta en bordes del hodoscopio (iteración 0.7).
// Para cortes 1D en y ∈ {0, ±10, ±14} mm:
//   Panel izquierdo: eficiencia geométrica vs x_true.
//   Panel derecho:   σ_x (RMS del residual) vs x_true, en bandas de 2 mm.
//
// Predicciones:
//   Eficiencia = 1 para |x| < 13.5 mm (zona activa), cae a 0 en los gaps.
//   σ_x ≈ 0.34 mm en zona central, puede degradarse en los últimos 2 mm.
//
// Uso desde build/:
//   root -l '../analysis/edge_response.C("xy_scan.root")'

#include <vector>
#include <cmath>
#include <map>

static double bar_center_x(int b) {
    if (b <  8) return -14.0 + 4.0 * b;
    if (b < 16) return -12.0 + 4.0 * (b - 8);
    return 0.;
}

struct RecoX { double x; int code; };
static RecoX reco_x(const Double_t edep[32], double thr) {
    RecoX r{NAN, 0};
    int bs = -1, bi = -1;
    double ms = thr, mi = thr;
    for (int b = 0; b <  8; ++b) if (edep[b] > ms) { ms = edep[b]; bs = b; }
    for (int b = 8; b < 16; ++b) if (edep[b] > mi) { mi = edep[b]; bi = b; }

    if (bs < 0 && bi < 0) return r;
    if (bs >= 0 && bi < 0) { r.x = bar_center_x(bs); r.code = 1; return r; }
    if (bs <  0 && bi >= 0){ r.x = bar_center_x(bi); r.code = 2; return r; }

    double cs = bar_center_x(bs), ci = bar_center_x(bi);
    double left = std::max(cs-1.5, ci-1.5), right = std::min(cs+1.5, ci+1.5);
    if (left > right) { r.x = (ms>mi)?cs:ci; r.code = 4; return r; }
    r.x = 0.5*(left+right); r.code = 3;
    return r;
}

// ---------------------------------------------------------------------------
void edge_response(const char* fname       = "xy_scan.root",
                   double       thresh_MeV  = 0.05,
                   double       band_width  = 2.0)
{
    TFile* f = TFile::Open(fname);
    if (!f || f->IsZombie()) { Printf("[ERROR] %s", fname); return; }
    TTree* t = (TTree*)f->Get("hodo");
    if (!t) { Printf("[ERROR] TTree 'hodo'"); return; }

    // Cortes en Y a analizar
    const std::vector<double> y_cuts = {0., 10., -10., 14., -14.};
    const double y_tol = 0.6;  // ± tolerancia en y para seleccionar el corte

    // Bins en x: de −15.5 a +15.5 en pasos de band_width
    const double xlo = -15.5, xhi = 15.5;
    const int    nx  = (int)std::round((xhi - xlo) / band_width);

    // Un par de histogramas por corte en y
    std::vector<TH1D*> h_eff(y_cuts.size()), h_sigma(y_cuts.size());
    std::vector<TH1D*> h_resid_sum(y_cuts.size()), h_resid2_sum(y_cuts.size());
    std::vector<TH1D*> h_nevents(y_cuts.size()), h_nov(y_cuts.size());

    int colors[] = {kBlack, kBlue+1, kBlue-4, kRed+1, kRed-4};
    for (size_t ic = 0; ic < y_cuts.size(); ++ic) {
        TString tag = Form("y%+.0f", y_cuts[ic]);
        h_eff[ic]        = new TH1D("eff_"  +tag, "", nx, xlo, xhi);
        h_resid_sum[ic]  = new TH1D("rsum_" +tag, "", nx, xlo, xhi);
        h_resid2_sum[ic] = new TH1D("r2sum_"+tag, "", nx, xlo, xhi);
        h_nevents[ic]    = new TH1D("nev_"  +tag, "", nx, xlo, xhi);
        h_sigma[ic]      = new TH1D("sig_"  +tag, "", nx, xlo, xhi);
        h_nov[ic] = new TH1D("nov_" +tag, "", nx, xlo, xhi);
        for (auto* h : {h_eff[ic], h_resid_sum[ic], h_resid2_sum[ic],
                         h_nevents[ic], h_sigma[ic], h_nov[ic]}) h->Sumw2(false);
    }

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
        for (size_t ic = 0; ic < y_cuts.size(); ++ic) {
            if (std::abs(prim_y - y_cuts[ic]) > y_tol) continue;

            auto rx = reco_x(edep, thresh_MeV);
            int  has_hit_x = (rx.code > 0) ? 1 : 0;

            // Eficiencia (requiere también hit en Y)
            int by_s = -1, by_i = -1;
            double my_s = thresh_MeV, my_i = thresh_MeV;
            for (int b = 16; b < 24; ++b) if (edep[b] > my_s) { my_s=edep[b]; by_s=b; }
            for (int b = 24; b < 32; ++b) if (edep[b] > my_i) { my_i=edep[b]; by_i=b; }
            int has_hit_y = (by_s >= 0 || by_i >= 0) ? 1 : 0;

            h_eff[ic]->Fill(prim_x, (double)(has_hit_x && has_hit_y));
            h_nevents[ic]->Fill(prim_x, 1.);

            // Residual: sólo para overlap (topology 3)
            if (rx.code == 3 && std::isfinite(rx.x)) {
                double res = rx.x - prim_x;
                h_resid_sum[ic] ->Fill(prim_x, res);
                h_resid2_sum[ic]->Fill(prim_x, res*res);
                h_nov[ic]       ->Fill(prim_x, 1.);
            }
        }
    }

    // Calcular eficiencia y σ_x por bin
    for (size_t ic = 0; ic < y_cuts.size(); ++ic) {
        for (int ix = 1; ix <= nx; ++ix) {
            double n = h_nevents[ic]->GetBinContent(ix);
            if (n < 5.) { h_eff[ic]->SetBinContent(ix, 0.); continue; }

            double eff_raw = h_eff[ic]->GetBinContent(ix) / n;
            h_eff[ic]->SetBinContent(ix, eff_raw);

            double n_ov = h_nov[ic]->GetBinContent(ix);
            double sum1 = h_resid_sum[ic] ->GetBinContent(ix);
            double sum2 = h_resid2_sum[ic]->GetBinContent(ix);
            if (n_ov > 5.) {
                // sigma² = <r²> - <r>²  (RMS del residual, no la desv. estándar)
                double rms = std::sqrt(sum2/n_ov);
                h_sigma[ic]->SetBinContent(ix, rms);
            }
        }
    }

    // --------------- Canvas 2 paneles ----------------------------------------
    gStyle->SetOptStat(0);

    TCanvas* c = new TCanvas("edge_resp", "Respuesta en bordes", 1400, 560);
    c->Divide(2, 1);

    // --- Panel 1: Eficiencia ---
    c->cd(1);
    gPad->SetLeftMargin(0.13);
    auto* frame1 = gPad->DrawFrame(-16., -0.05, 16., 1.15,
                                    "Eficiencia geom#acute{e}trica vs x_{true};"
                                    "x_{true} [mm];P(hit_{X} AND hit_{Y})");
    frame1->GetXaxis()->SetTitleSize(0.05);
    frame1->GetYaxis()->SetTitleSize(0.05);

    TLegend* leg1 = new TLegend(0.55, 0.18, 0.92, 0.48);
    leg1->SetBorderSize(0); leg1->SetFillStyle(0); leg1->SetTextSize(0.035);

    for (size_t ic = 0; ic < y_cuts.size(); ++ic) {
        h_eff[ic]->SetLineColor(colors[ic]);
        h_eff[ic]->SetLineWidth(2);
        h_eff[ic]->Draw("HIST SAME");
        leg1->AddEntry(h_eff[ic], Form("y = %+.0f mm", y_cuts[ic]), "l");
    }
    leg1->Draw();

    // Línea de referencia en 1
    auto* ln1 = new TLine(-16., 1., 16., 1.);
    ln1->SetLineStyle(2); ln1->SetLineColor(kGray+1); ln1->Draw();

    // --- Panel 2: σ_x ---
    c->cd(2);
    gPad->SetLeftMargin(0.13);
    auto* frame2 = gPad->DrawFrame(-16., 0., 16., 1.5,
                                    "#sigma_{x} vs x_{true} (top. 3);"
                                    "x_{true} [mm];#sigma_{x} [mm]");
    frame2->GetXaxis()->SetTitleSize(0.05);
    frame2->GetYaxis()->SetTitleSize(0.05);

    // Línea de referencia σ_x = 0.337 mm (resultado iteración 0.5)
    auto* ref = new TLine(-16., 0.337, 16., 0.337);
    ref->SetLineStyle(2); ref->SetLineColor(kRed+1); ref->SetLineWidth(2); ref->Draw();

    TLegend* leg2 = new TLegend(0.55, 0.7, 0.92, 0.92);
    leg2->SetBorderSize(0); leg2->SetFillStyle(0); leg2->SetTextSize(0.035);
    leg2->AddEntry(ref, "#sigma_{x} ref = 0.337 mm", "l");

    for (size_t ic = 0; ic < y_cuts.size(); ++ic) {
        h_sigma[ic]->SetLineColor(colors[ic]);
        h_sigma[ic]->SetLineWidth(2);
        h_sigma[ic]->Draw("HIST SAME");
        leg2->AddEntry(h_sigma[ic], Form("y = %+.0f mm", y_cuts[ic]), "l");
    }
    leg2->Draw();

    c->SaveAs("edge_response.png");
    Printf("Figura guardada: edge_response.png");

    f->Close();
}
