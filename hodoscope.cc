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
//   * G4RunManagerFactory selecciona automáticamente RunManager serial o MT.
//   * Forzamos modo serial inicialmente para depurar; luego se puede liberar.
//----------------------------------------------------------------------------

#include "G4RunManagerFactory.hh"
#include "G4UImanager.hh"
#include "G4VisExecutive.hh"
#include "G4UIExecutive.hh"
#include "Randomize.hh"

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

  // ----- Run manager (serial por ahora) -------------------------------------
  auto* runManager =
    G4RunManagerFactory::CreateRunManager(G4RunManagerType::Serial);

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
