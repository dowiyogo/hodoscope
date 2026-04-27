//----------------------------------------------------------------------------
// RunAction.cc
//----------------------------------------------------------------------------
#include "RunAction.hh"
#include "G4AnalysisManager.hh"
#include "G4Run.hh"
#include "G4SystemOfUnits.hh"
#include "G4Threading.hh"
#include <sstream>
#include <iomanip>

namespace {
  G4String idxName(const G4String& base, int i) {
    std::ostringstream oss;
    oss << base << std::setw(2) << std::setfill('0') << i;
    return G4String(oss.str());
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

  if (fIsMaster) {
    // Maestro: abrir el archivo principal sólo en el primer run.
    if (an->GetFileName().empty()) an->SetFileName("hodoscope");
    if (!fFileOpen) {
      an->OpenFile();
      fFileOpen        = true;
      fCurrentFileName = an->GetFileName();
      G4cout << "[RunAction] Output file: " << fCurrentFileName << G4endl;
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
