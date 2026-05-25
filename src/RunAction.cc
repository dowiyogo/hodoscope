//----------------------------------------------------------------------------
// RunAction.cc
//----------------------------------------------------------------------------
#include "RunAction.hh"
#include "G4AnalysisManager.hh"
#include "G4Run.hh"
#include "G4RunManager.hh"
#include "G4SystemOfUnits.hh"
#include "G4Threading.hh"
#include "DetectorConstruction.hh"

#include <fstream>
#include <sstream>
#include <iomanip>

namespace {
  G4String idxName(const G4String& base, int i) {
    std::ostringstream oss;
    oss << base << std::setw(2) << std::setfill('0') << i;
    return G4String(oss.str());
  }

  G4String makeConfigSidecarName(const G4String& rootFileName)
  {
    std::string path(rootFileName);
    if (path.size() >= 5 && path.substr(path.size() - 5) == ".root") {
      path.resize(path.size() - 5);
    }
    return G4String(path + "_config.txt");
  }

  void writeVariantSidecar(const G4String& rootFileName,
            const DetectorConstruction& det)
  {
    const auto& cfg = det.GetDetectorVariantConfig();
    std::ofstream out(makeConfigSidecarName(rootFileName));
    if (!out) {
      G4cerr << "[RunAction] Could not create detector config sidecar for "
        << rootFileName << G4endl;
      return;
    }

    out << "detector_variant=" << cfg.variantLabel << '\n'
   << "scintillator_material=" << cfg.scintillatorMaterial << '\n'
   << "reflector_name=" << cfg.reflectorName << '\n'
   << "reflector_model=" << cfg.reflectorModel << '\n'
   << "reflector_thickness_mm=" << cfg.reflectorThicknessMm / mm << '\n'
   << "kapton_thickness_mm=" << cfg.kaptonThicknessMm / mm << '\n'
   << "mppc_model=" << cfg.mppcModel << '\n'
   << "physical_layer_enabled=" << (cfg.physicalLayerEnabled ? "true" : "false") << '\n'
   << "optical_photons_enabled=" << (det.IsOpticalEnabled() ? "true" : "false") << '\n'
   << "improved_optical_coupling="
   << (det.IsImprovedOpticalCouplingEnabled() ? "true" : "false") << '\n'
   << "reflector_debug_mode=" << det.GetReflectorDebugMode() << '\n'
   << "tio2_epoxy_effective_r425=" << det.GetTio2EpoxyEffectiveR425() << '\n'
   << "tio2_epoxy_surface_mode=" << det.GetTio2EpoxySurfaceMode() << '\n';
  }

  void logVariantSummary(const DetectorConstruction& det)
  {
    const auto& cfg = det.GetDetectorVariantConfig();
    G4cout << "[RunAction] Detector variant selected: "
      << cfg.variantLabel << G4endl;
    G4cout << "[RunAction] Scintillator material: "
      << cfg.scintillatorMaterial << G4endl;
    G4cout << "[RunAction] Reflector type: "
      << cfg.reflectorName << G4endl;
    G4cout << "[RunAction] Reflector thickness: "
      << cfg.reflectorThicknessMm / mm << " mm" << G4endl;
    G4cout << "[RunAction] Kapton thickness: "
      << cfg.kaptonThicknessMm / mm << " mm" << G4endl;
    G4cout << "[RunAction] Reflector model: "
      << cfg.reflectorModel << G4endl;
    G4cout << "[RunAction] Physical layer enabled: "
      << (cfg.physicalLayerEnabled ? "yes" : "no") << G4endl;
    G4cout << "[RunAction] Optical photons: "
      << (det.IsOpticalEnabled() ? "enabled" : "disabled") << G4endl;
    G4cout << "[RunAction] Improved optical coupling: "
      << (det.IsImprovedOpticalCouplingEnabled() ? "enabled" : "disabled") << G4endl;
    G4cout << "[RunAction] Reflector debug mode: "
      << det.GetReflectorDebugMode() << G4endl;
    G4cout << "[RunAction] TiO2+epoxy effective R425: ";
    if (det.GetTio2EpoxyEffectiveR425() < 0.0) G4cout << "disabled";
    else G4cout << det.GetTio2EpoxyEffectiveR425();
    G4cout << G4endl;
    G4cout << "[RunAction] TiO2+epoxy surface mode: "
      << det.GetTio2EpoxySurfaceMode() << G4endl;
  }
}

RunAction::RunAction() : G4UserRunAction(),
  fIsMaster(G4Threading::IsMasterThread())
{
  auto* an = G4AnalysisManager::Instance();
  an->SetDefaultFileType("root");
  an->SetVerboseLevel(1);
  an->SetNtupleMerging(true);  // requerido para MT; no-op en modo serial

  // ----- Definir el TTree y sus branches -----------------------------------
  // Se guardan como columnas individuales por simplicidad (no arrays G4-style).
  an->CreateNtuple("hodo", "Hodoscope per-event tree");

  // 0..6: primario
  an->CreateNtupleIColumn("eventID");
  an->CreateNtupleDColumn("prim_x");      // mm
  an->CreateNtupleDColumn("prim_y");
  an->CreateNtupleDColumn("prim_z");
  an->CreateNtupleDColumn("prim_px");
  an->CreateNtupleDColumn("prim_py");
  an->CreateNtupleDColumn("prim_pz");
  an->CreateNtupleDColumn("prim_E");      // MeV

  // 8..39: edep[32]
  for (int i = 0; i < 32; ++i)
    an->CreateNtupleDColumn(idxName("edep_", i));

  // 40..71: nph[32]
  for (int i = 0; i < 32; ++i)
    an->CreateNtupleIColumn(idxName("nph_", i));

  // 72..103: tfirst[32]
  for (int i = 0; i < 32; ++i)
    an->CreateNtupleDColumn(idxName("tfirst_", i));

  an->FinishNtuple();
}

void RunAction::BeginOfRunAction(const G4Run* /*run*/)
{
  auto* an = G4AnalysisManager::Instance();
  const auto* det = dynamic_cast<const DetectorConstruction*>(
      G4RunManager::GetRunManager()->GetUserDetectorConstruction());

  if (fIsMaster) {
    // Maestro: abrir el archivo principal sólo en el primer run.
    if (an->GetFileName().empty()) an->SetFileName("hodoscope");
    if (!fFileOpen) {
      an->OpenFile();
      fFileOpen        = true;
      fCurrentFileName = an->GetFileName();
      G4cout << "[RunAction] Output file: " << fCurrentFileName << G4endl;
      if (det) {
        logVariantSummary(*det);
        writeVariantSidecar(fCurrentFileName, *det);
      }
    }
    // fAllowFileCycling=false en MT → ciclado desactivado.
  } else {
    // Workers: abrir un buffer temporal fresco en cada run.
    // (fFileOpen=false fue restablecido en el EndOfRunAction anterior)
    an->OpenFile();
    fFileOpen = true;
  }
}

void RunAction::EndOfRunAction(const G4Run* /*run*/)
{
  auto* an = G4AnalysisManager::Instance();
  if (fIsMaster) {
    // Maestro: recoger los datos de los workers (ya escribieron y cerraron
    // sus buffers) y volcarlos al archivo principal. El archivo permanece
    // abierto para acumular el siguiente run.
    if (fFileOpen) an->Write();
  } else {
    // Workers: vaciar filas al buffer de merge y cerrarlo. El maestro
    // llamará Write() después para recoger estos datos.
    an->Write();
    an->CloseFile(false);  // conserva defs de columnas; fFileOpen se resetea
    fFileOpen = false;
  }
}

RunAction::~RunAction()
{
  // El archivo del maestro se cierra explícitamente desde main() antes de
  // destruir el runManager (mientras los workers aún existen). Los workers
  // ya cerraron sus buffers en EndOfRunAction. Nada que hacer aquí.
}
