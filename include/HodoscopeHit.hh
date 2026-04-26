//----------------------------------------------------------------------------
// HodoscopeHit.hh
//
// Hit genérico para barras y para SiPMs.
//
// Para barras (kBar):
//   - copyNo  : 0..31 (ID global de barra)
//   - edep    : energía depositada [MeV]
//   - posEntry: punto de entrada del primario al volumen
//   - posExit : punto de salida
//   - tFirst  : tiempo del primer hit
//
// Para SiPMs (kSiPM, futura propagación óptica):
//   - copyNo  : 0..31 (ID global de SiPM, asociado 1:1 con la barra)
//   - nPhotons: contador de fotones que atraviesan el volumen
//
// Este diseño permite extender hacia hits ópticos sin reescribir la clase.
//----------------------------------------------------------------------------
#ifndef HODOSCOPE_HIT_HH
#define HODOSCOPE_HIT_HH

#include "G4VHit.hh"
#include "G4THitsCollection.hh"
#include "G4Allocator.hh"
#include "G4ThreeVector.hh"
#include "globals.hh"

enum class HitType { kBar, kSiPM };

class HodoscopeHit : public G4VHit
{
public:
  HodoscopeHit() = default;
  ~HodoscopeHit() override = default;

  inline void* operator new(size_t);
  inline void  operator delete(void*);

  // ---- public data (datos planos para acceso eficiente) -------------------
  HitType        type      = HitType::kBar;
  G4int          copyNo    = -1;
  G4double       edep      = 0.;
  G4int          nPhotons  = 0;
  G4double       tFirst    = 0.;
  G4ThreeVector  posEntry  = G4ThreeVector();
  G4ThreeVector  posExit   = G4ThreeVector();
};

using HodoscopeHitsCollection = G4THitsCollection<HodoscopeHit>;

extern G4ThreadLocal G4Allocator<HodoscopeHit>* HodoscopeHitAllocator;

inline void* HodoscopeHit::operator new(size_t)
{
  if (!HodoscopeHitAllocator)
    HodoscopeHitAllocator = new G4Allocator<HodoscopeHit>;
  return (void*)HodoscopeHitAllocator->MallocSingle();
}

inline void HodoscopeHit::operator delete(void* h)
{
  HodoscopeHitAllocator->FreeSingle((HodoscopeHit*)h);
}

#endif
