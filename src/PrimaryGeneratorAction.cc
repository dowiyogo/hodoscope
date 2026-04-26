//----------------------------------------------------------------------------
// PrimaryGeneratorAction.cc
//----------------------------------------------------------------------------
#include "PrimaryGeneratorAction.hh"

#include "G4ParticleGun.hh"
#include "G4ParticleTable.hh"
#include "G4Event.hh"
#include "G4SystemOfUnits.hh"
#include "G4ThreeVector.hh"

PrimaryGeneratorAction::PrimaryGeneratorAction()
: G4VUserPrimaryGeneratorAction(), fGun(nullptr)
{
  fGun = new G4ParticleGun(1);

  auto* table = G4ParticleTable::GetParticleTable();
  fGun->SetParticleDefinition(table->FindParticle("mu-"));
  fGun->SetParticleEnergy(4.0 * GeV);                 // MIP por defecto
  fGun->SetParticlePosition(G4ThreeVector(0., 0., 50.*mm));   // arriba del detector
  fGun->SetParticleMomentumDirection(G4ThreeVector(0., 0., -1.));
}

PrimaryGeneratorAction::~PrimaryGeneratorAction()
{
  delete fGun;
}

void PrimaryGeneratorAction::GeneratePrimaries(G4Event* anEvent)
{
  fGun->GeneratePrimaryVertex(anEvent);
}
