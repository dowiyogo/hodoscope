#include <TBranch.h>
#include <TClass.h>
#include <TFile.h>
#include <TKey.h>
#include <TTree.h>

#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

struct VariantSummary {
  std::string label;
  std::string file;
  std::string tree;
  Long64_t events = 0;
  Long64_t totalNph = 0;
  double meanNph = 0.0;
  Long64_t maxNph = 0;
  Long64_t eventsWithNph = 0;
  double fractionEventsWithNph = 0.0;
};

TTree* FindTree(TFile* file, std::string& treeName)
{
  if (auto* tree = dynamic_cast<TTree*>(file->Get("hodo"))) {
    treeName = "hodo";
    return tree;
  }

  TIter next(file->GetListOfKeys());
  while (auto* obj = next()) {
    auto* key = dynamic_cast<TKey*>(obj);
    if (!key) continue;
    auto* cl = TClass::GetClass(key->GetClassName());
    if (!cl || !cl->InheritsFrom(TTree::Class())) continue;

    treeName = key->GetName();
    return dynamic_cast<TTree*>(file->Get(treeName.c_str()));
  }

  throw std::runtime_error("No TTree found in " + std::string(file->GetName()));
}

VariantSummary SummarizeVariant(const std::string& label, const std::string& path)
{
  auto* file = TFile::Open(path.c_str(), "READ");
  if (!file || file->IsZombie()) {
    throw std::runtime_error("Could not open " + path);
  }

  VariantSummary summary;
  summary.label = label;
  summary.file = path;
  auto* tree = FindTree(file, summary.tree);
  summary.events = tree->GetEntries();

  std::vector<Int_t> nph(32, 0);
  for (int i = 0; i < 32; ++i) {
    const auto branchName = Form("nph_%02d", i);
    if (!tree->GetBranch(branchName)) {
      throw std::runtime_error("Missing branch " + std::string(branchName));
    }
    tree->SetBranchAddress(branchName, &nph[i]);
  }

  for (Long64_t entry = 0; entry < summary.events; ++entry) {
    tree->GetEntry(entry);
    Long64_t eventNph = 0;
    for (const auto value : nph) eventNph += value;

    summary.totalNph += eventNph;
    if (eventNph > summary.maxNph) summary.maxNph = eventNph;
    if (eventNph > 0) ++summary.eventsWithNph;
  }

  if (summary.events > 0) {
    summary.meanNph = static_cast<double>(summary.totalNph) / summary.events;
    summary.fractionEventsWithNph =
      static_cast<double>(summary.eventsWithNph) / summary.events;
  }

  file->Close();
  return summary;
}

void WriteSummary(std::ostream& out, const VariantSummary& summary)
{
  out << summary.label << ":\n"
      << "  file: " << summary.file << "\n"
      << "  tree: " << summary.tree << "\n"
      << "  events: " << summary.events << "\n"
      << "  total_nph: " << summary.totalNph << "\n"
      << "  mean_nph_per_event: " << summary.meanNph << "\n"
      << "  max_nph_per_event: " << summary.maxNph << "\n"
      << "  events_with_nph_gt_0: " << summary.eventsWithNph << "\n"
      << "  fraction_events_with_nph_gt_0: "
      << summary.fractionEventsWithNph << "\n\n";
}

void compare_variant_nph()
{
  const std::string tio2Path =
    "diagnostics/optical_variant_comparison/outputs/variant_tio2_quick.root";
  const std::string vikuitiPath =
    "diagnostics/optical_variant_comparison/outputs/variant_vikuiti_quick.root";
  const std::string outputPath =
    "diagnostics/optical_variant_comparison/variant_nph_comparison.txt";

  const auto tio2 = SummarizeVariant("TiO2", tio2Path);
  const auto vikuiti = SummarizeVariant("Vikuiti", vikuitiPath);
  const auto ratio =
    tio2.meanNph > 0.0 ? vikuiti.meanNph / tio2.meanNph : INFINITY;

  std::ofstream out(outputPath);
  if (!out) {
    throw std::runtime_error("Could not write " + outputPath);
  }

  out << std::setprecision(10);
  std::cout << std::setprecision(10);

  auto writeAll = [&](std::ostream& stream) {
    stream << "Optical variant nph comparison\n\n";
    WriteSummary(stream, tio2);
    WriteSummary(stream, vikuiti);
    stream << "ratio_mean_vikuiti_over_tio2: " << ratio << "\n"
           << "vikuiti_gt_tio2: " << (vikuiti.meanNph > tio2.meanNph ? "true" : "false") << "\n"
           << "ratio_in_expected_range_1p3_to_2p0: "
           << (ratio >= 1.3 && ratio <= 2.0 ? "true" : "false") << "\n";
  };

  writeAll(out);
  writeAll(std::cout);
}
