#include <TBranch.h>
#include <TClass.h>
#include <TFile.h>
#include <TKey.h>
#include <TTree.h>

#include <algorithm>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

struct ReflectorModeSummary {
  std::string label;
  std::string file;
  std::string tree;
  Long64_t events = 0;
  Long64_t totalNph = 0;
  double meanNph = 0.0;
  double medianNph = 0.0;
  Long64_t maxNph = 0;
  Long64_t eventsWithNph = 0;
  double fractionEventsWithNph = 0.0;
  double meanEdep = 0.0;
  bool hasEdep = false;
};

TTree* FindReflectorTree(TFile* file, std::string& treeName)
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

double Median(std::vector<Long64_t> values)
{
  if (values.empty()) return 0.0;
  std::sort(values.begin(), values.end());
  const auto mid = values.size() / 2;
  if (values.size() % 2 == 1) return static_cast<double>(values[mid]);
  return 0.5 * static_cast<double>(values[mid - 1] + values[mid]);
}

ReflectorModeSummary SummarizeReflectorMode(const std::string& label,
                                             const std::string& path)
{
  auto* file = TFile::Open(path.c_str(), "READ");
  if (!file || file->IsZombie()) {
    throw std::runtime_error("Could not open " + path);
  }

  ReflectorModeSummary summary;
  summary.label = label;
  summary.file = path;
  auto* tree = FindReflectorTree(file, summary.tree);
  summary.events = tree->GetEntries();

  std::vector<Int_t> nph(32, 0);
  std::vector<Double_t> edep(32, 0.0);
  for (int i = 0; i < 32; ++i) {
    const auto nphBranchName = Form("nph_%02d", i);
    if (!tree->GetBranch(nphBranchName)) {
      throw std::runtime_error("Missing branch " + std::string(nphBranchName));
    }
    tree->SetBranchAddress(nphBranchName, &nph[i]);

    const auto edepBranchName = Form("edep_%02d", i);
    if (tree->GetBranch(edepBranchName)) {
      tree->SetBranchAddress(edepBranchName, &edep[i]);
      summary.hasEdep = true;
    }
  }

  std::vector<Long64_t> eventNphValues;
  eventNphValues.reserve(summary.events);
  double totalEdep = 0.0;

  for (Long64_t entry = 0; entry < summary.events; ++entry) {
    tree->GetEntry(entry);
    Long64_t eventNph = 0;
    double eventEdep = 0.0;

    for (int i = 0; i < 32; ++i) {
      eventNph += nph[i];
      if (summary.hasEdep) eventEdep += edep[i];
    }

    eventNphValues.push_back(eventNph);
    summary.totalNph += eventNph;
    if (eventNph > summary.maxNph) summary.maxNph = eventNph;
    if (eventNph > 0) ++summary.eventsWithNph;
    totalEdep += eventEdep;
  }

  if (summary.events > 0) {
    summary.meanNph = static_cast<double>(summary.totalNph) / summary.events;
    summary.medianNph = Median(eventNphValues);
    summary.fractionEventsWithNph =
      static_cast<double>(summary.eventsWithNph) / summary.events;
    if (summary.hasEdep) summary.meanEdep = totalEdep / summary.events;
  }

  file->Close();
  return summary;
}

void WriteReflectorSummary(std::ostream& out, const ReflectorModeSummary& summary)
{
  out << summary.label << ":\n"
      << "  file: " << summary.file << "\n"
      << "  tree: " << summary.tree << "\n"
      << "  events: " << summary.events << "\n"
      << "  total_nph: " << summary.totalNph << "\n"
      << "  mean_nph_per_event: " << summary.meanNph << "\n"
      << "  median_nph_per_event: " << summary.medianNph << "\n"
      << "  max_nph_per_event: " << summary.maxNph << "\n"
      << "  events_with_nph_gt_0: " << summary.eventsWithNph << "\n"
      << "  fraction_events_with_nph_gt_0: "
      << summary.fractionEventsWithNph << "\n"
      << "  mean_edep_per_event: "
      << (summary.hasEdep ? std::to_string(summary.meanEdep) : "not_available")
      << "\n\n";
}

double Ratio(double numerator, double denominator)
{
  return denominator > 0.0 ? numerator / denominator : INFINITY;
}

void compare_reflector_debug_modes()
{
  const auto mode1 = SummarizeReflectorMode(
    "mode1_tio2R_diffuse",
    "diagnostics/optical_variant_ratio_debug/outputs/mode1_tio2R_diffuse.root");
  const auto mode2 = SummarizeReflectorMode(
    "mode2_esrR_diffuse",
    "diagnostics/optical_variant_ratio_debug/outputs/mode2_esrR_diffuse.root");
  const auto mode3 = SummarizeReflectorMode(
    "mode3_tio2R_specular",
    "diagnostics/optical_variant_ratio_debug/outputs/mode3_tio2R_specular.root");
  const auto mode4 = SummarizeReflectorMode(
    "mode4_esrR_specular",
    "diagnostics/optical_variant_ratio_debug/outputs/mode4_esrR_specular.root");

  const std::string outputPath =
    "diagnostics/optical_variant_ratio_debug/reflector_debug_matrix.txt";
  std::ofstream out(outputPath);
  if (!out) {
    throw std::runtime_error("Could not write " + outputPath);
  }

  out << std::setprecision(10);
  std::cout << std::setprecision(10);

  auto writeAll = [&](std::ostream& stream) {
    stream << "Reflector debug matrix\n\n";
    WriteReflectorSummary(stream, mode1);
    WriteReflectorSummary(stream, mode2);
    WriteReflectorSummary(stream, mode3);
    WriteReflectorSummary(stream, mode4);
    stream << "ratio_mode2_over_mode1_reflectivity_effect_diffuse: "
           << Ratio(mode2.meanNph, mode1.meanNph) << "\n"
           << "ratio_mode3_over_mode1_angular_surface_effect_tio2R: "
           << Ratio(mode3.meanNph, mode1.meanNph) << "\n"
           << "ratio_mode4_over_mode3_reflectivity_effect_specular: "
           << Ratio(mode4.meanNph, mode3.meanNph) << "\n"
           << "ratio_mode4_over_mode1_total_effect: "
           << Ratio(mode4.meanNph, mode1.meanNph) << "\n";
  };

  writeAll(out);
  writeAll(std::cout);
}
