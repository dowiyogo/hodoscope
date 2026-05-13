//----------------------------------------------------------------------------
// hodoscope.cc
//
// Programa principal de la simulación Geant4 del hodoscopio NA64-mini
// para muografía geológica (Universidad de La Serena).
//
// Uso:
//   ./hodoscope                       -> abre UI interactivo (vis.mac)
//   ./hodoscope macros/script.mac     -> modo batch
//
// Diseño:
//   * G4RunManagerType::Default → MT con min(8, hardware_concurrency) hilos.
//   * En modo batch, CloseFile() se llama explícitamente antes de destruir
//     el runManager para que el merge final de NTuples sea correcto (G4 gotcha 4).
//----------------------------------------------------------------------------

#include "G4RunManagerFactory.hh"
#include "G4UImanager.hh"
#include "G4VisExecutive.hh"
#include "G4UIExecutive.hh"
#include "G4AnalysisManager.hh"
#include "Randomize.hh"
#include <cstdlib>
#include <thread>

#include "DetectorConstruction.hh"
#include "PhysicsList.hh"
#include "ActionInitialization.hh"

int main(int argc, char** argv)
{
  // ----- Semilla aleatoria reproducible salvo override en macro -------------
  G4Random::setTheEngine(new CLHEP::RanecuEngine);
  G4long seed = 1234567;
  G4Random::setTheSeed(seed);

  // ----- UI executive sólo si no se pasó macro ------------------------------
  G4UIExecutive* ui = nullptr;
  if (argc == 1) {
    ui = new G4UIExecutive(argc, argv);
  }

  // ----- Run manager multihilo -----------------------------------------------
  auto* runManager =
    G4RunManagerFactory::CreateRunManager(G4RunManagerType::Default);
  G4int nThreads = std::min(8, (G4int)std::thread::hardware_concurrency());
  if (nThreads < 1) nThreads = 1;
  if (const char* envThreads = std::getenv("HODO_THREADS")) {
    const G4int requestedThreads = std::atoi(envThreads);
    if (requestedThreads > 0) {
      nThreads = requestedThreads;
    } else {
      G4cerr << "[main] Ignoring invalid HODO_THREADS="
             << envThreads << G4endl;
    }
  }
  runManager->SetNumberOfThreads(nThreads);
  G4cout << "[main] Geant4 running with " << nThreads << " threads" << G4endl;

  // ----- Inicialización del usuario -----------------------------------------
  runManager->SetUserInitialization(new DetectorConstruction());
  runManager->SetUserInitialization(new PhysicsList());
  runManager->SetUserInitialization(new ActionInitialization());

  // ----- Visualización ------------------------------------------------------
  auto* visManager = new G4VisExecutive("Quiet");
  visManager->Initialize();

  auto* UImanager = G4UImanager::GetUIpointer();

  if (!ui) {
    // Modo batch: ejecutar macro pasado como argumento
    G4String command  = "/control/execute ";
    G4String fileName = argv[1];
    UImanager->ApplyCommand(command + fileName);

    // Cerrar el archivo de análisis ANTES de destruir el runManager.
    // En MT, workers aún existen en este punto; CloseFile() puede completar
    // el merge final sin encontrar buffers ya liberados.
    auto* an = G4AnalysisManager::Instance();
    if (an) { an->Write(); an->CloseFile(); }
    G4cout << "[main] Analysis file closed." << G4endl;
  } else {
    // Modo interactivo: lanzar vis.mac y abrir UI
    UImanager->ApplyCommand("/control/execute init_vis.mac");
    ui->SessionStart();
    delete ui;
  }

  // ----- Liberación ---------------------------------------------------------
  delete visManager;
  delete runManager;
  return 0;
}
