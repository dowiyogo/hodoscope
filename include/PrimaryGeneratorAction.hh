//----------------------------------------------------------------------------
// PrimaryGeneratorAction.hh
//
// Generador primario simple basado en G4ParticleGun.
//
// Uso desde macro: comandos estándar /gun/...
//   /gun/particle mu-
//   /gun/energy 4.0 GeV
//   /gun/position 0.0 0.0 50.0 mm
//   /gun/direction 0.0 0.0 -1.0
//
// Para escanear se usa /control/loop sobre /gun/position en macros.
// (Ver macros/scan_xy.mac.)
//----------------------------------------------------------------------------
#ifndef HODOSCOPE_PRIMARY_GENERATOR_ACTION_HH
#define HODOSCOPE_PRIMARY_GENERATOR_ACTION_HH

#include "G4VUserPrimaryGeneratorAction.hh"
#include "globals.hh"

class G4ParticleGun;
class G4Event;

class PrimaryGeneratorAction : public G4VUserPrimaryGeneratorAction
{
public:
  PrimaryGeneratorAction();
  ~PrimaryGeneratorAction() override;

  void GeneratePrimaries(G4Event* anEvent) override;

  // accesos (útil para EventAction al guardar info de la partícula primaria)
  const G4ParticleGun* GetParticleGun() const { return fGun; }

private:
  G4ParticleGun* fGun;
};

#endif
