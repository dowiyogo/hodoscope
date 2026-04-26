//----------------------------------------------------------------------------
// PhysicsList.hh
//
// Lista de física basada en FTFP_BERT (estándar Geant4 para cosmics/HEP)
// + G4OpticalPhysics opcional (preparado para encender el camino óptico).
//----------------------------------------------------------------------------
#ifndef HODOSCOPE_PHYSICS_LIST_HH
#define HODOSCOPE_PHYSICS_LIST_HH

#include "G4VModularPhysicsList.hh"

class PhysicsList : public G4VModularPhysicsList
{
public:
  PhysicsList();
  ~PhysicsList() override = default;

  void SetCuts() override;
};

#endif
