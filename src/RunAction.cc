//----------------------------------------------------------------------------
// RunAction.cc
//----------------------------------------------------------------------------
#include "RunAction.hh"
#include "G4AnalysisManager.hh"
#include "G4Run.hh"
#include "G4SystemOfUnits.hh"
#include <sstream>
#include <iomanip>

namespace {
  G4String idxName(const G4String& base, int i) {
    std::ostringstream oss;
    oss << base << std::setw(2) << std::setfill('0') << i;
    return G4String(oss.str());
  }
}

RunAction::RunAction() : G4UserRunAction()
{
  auto* an = G4AnalysisManager::Instance();
  an->SetDefaultFileType("root");
  an->SetVerboseLevel(1);
  // SetNtupleMerging(true) se reserva para modo MT; en modo secuencial
  // interfiere con el ciclado manual de archivos (CloseFile+OpenFile por D).

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

  // Default si el macro no llama /analysis/setFileName.
  if (an->GetFileName().empty()) an->SetFileName("hodoscope");
  G4String reqName = an->GetFileName();

  if (!fFileOpen) {
    // Primer run de la sesión: abrir el archivo.
    an->OpenFile();
    fFileOpen        = true;
    // Guardamos el nombre POST-apertura (GetFileName() devuelve "name.root" tras OpenFile).
    fCurrentFileName = an->GetFileName();
    G4cout << "[RunAction] Output file: " << fCurrentFileName << G4endl;
  } else if (reqName != fCurrentFileName) {
    // El macro cambió /analysis/setFileName (nuevo valor de D en el barrido):
    // cerrar el archivo actual y abrir uno nuevo con el mismo esquema de NTuple.
    // CloseFile(false) conserva las definiciones de columnas para el próximo OpenFile().
    an->Write();
    an->CloseFile(false);
    an->OpenFile();
    fCurrentFileName = an->GetFileName();   // nombre post-apertura con extensión
    G4cout << "[RunAction] Switching output file: " << fCurrentFileName << G4endl;
  }
  // Si reqName == fCurrentFileName: mismo archivo, sigue acumulando eventos.
}

void RunAction::EndOfRunAction(const G4Run* /*run*/)
{
  // NO cerramos el file aquí: lo dejamos abierto para los siguientes runs.
  // El cierre real ocurre en el destructor (al terminar el programa).
}

RunAction::~RunAction()
{
  if (fFileOpen) {
    auto* an = G4AnalysisManager::Instance();
    an->Write();
    an->CloseFile();
    G4cout << "[RunAction] Output file closed and written." << G4endl;
  }
}
