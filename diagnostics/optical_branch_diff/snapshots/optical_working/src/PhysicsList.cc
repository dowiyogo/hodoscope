//----------------------------------------------------------------------------
// PhysicsList.cc
//
// Composición:
//   - G4DecayPhysics                  decaimientos
//   - G4RadioactiveDecayPhysics       no esencial pero sin costo apreciable
//   - G4EmStandardPhysics_option4     EM precisa
//   - FTFP_BERT-like hadronic         (vía G4HadronPhysicsFTFP_BERT, etc.)
//   - G4OpticalPhysics                preparado, registrado pero deshabilitado
//                                     por defecto a través del flag externo.
//
// Para muones MIP el dE/dx viene de G4EmStandardPhysics_option4. Con
// G4UserLimits(MaxStep=0.1mm) en la barra (1 mm), garantizamos varios pasos
// dentro del centellador.
//----------------------------------------------------------------------------
#include "PhysicsList.hh"

#include "G4DecayPhysics.hh"
#include "G4RadioactiveDecayPhysics.hh"
#include "G4EmStandardPhysics_option4.hh"
#include "G4HadronPhysicsFTFP_BERT.hh"
#include "G4HadronElasticPhysics.hh"
#include "G4StoppingPhysics.hh"
#include "G4IonPhysics.hh"
#include "G4OpticalPhysics.hh"
#include "G4SystemOfUnits.hh"

PhysicsList::PhysicsList() : G4VModularPhysicsList()
{
  SetVerboseLevel(1);

  RegisterPhysics(new G4DecayPhysics());
  RegisterPhysics(new G4RadioactiveDecayPhysics());
  RegisterPhysics(new G4EmStandardPhysics_option4());
  RegisterPhysics(new G4HadronElasticPhysics());
  RegisterPhysics(new G4HadronPhysicsFTFP_BERT());
  RegisterPhysics(new G4StoppingPhysics());
  RegisterPhysics(new G4IonPhysics());

  // Optical physics: register only if HODO_ENABLE_OPTICAL=1 in env.
  // This allows running Iteration 0 (optical off) unchanged while enabling
  // a minimal optical transport for Iteration 1 when requested.
  const char* env_opt = std::getenv("HODO_ENABLE_OPTICAL");
  if (env_opt && std::string(env_opt) == "1") {
    auto* op = new G4OpticalPhysics();
    RegisterPhysics(op);
    G4cout << "[PhysicsList] G4OpticalPhysics registered (HODO_ENABLE_OPTICAL=1)" << G4endl;
  } else {
    G4cout << "[PhysicsList] G4OpticalPhysics NOT registered (HODO_ENABLE_OPTICAL!=1)" << G4endl;
  }
}

void PhysicsList::SetCuts()
{
  // Cuts globales por rango: 0.1 mm (electrones, photones, positrones)
  defaultCutValue = 0.1 * mm;
  SetCutValue(defaultCutValue, "gamma");
  SetCutValue(defaultCutValue, "e-");
  SetCutValue(defaultCutValue, "e+");
}
