//----------------------------------------------------------------------------
// SiPMSD.hh
//
// Sensitive detector "frontera lógica" para los 32 SiPMs.
//
// FASE ACTUAL (sin fotones ópticos):
//   - Sin propagación óptica activa, no llegan opticalphotons al SD.
//   - Mantenemos el SD listo: cuando se active G4OpticalPhysics, contará
//     fotones ópticos que entren al volumen.
//
// FASE FUTURA (con G4OpticalPhysics activado):
//   - cada step de un G4OpticalPhoton dentro del SiPM_LV → nPhotons++
//   - permite estimar resolución temporal y carga proporcional al edep.
//----------------------------------------------------------------------------
#ifndef HODOSCOPE_SIPM_SD_HH
#define HODOSCOPE_SIPM_SD_HH

#include "G4VSensitiveDetector.hh"
#include "HodoscopeHit.hh"
#include <array>

class G4Step;
class G4HCofThisEvent;

class SiPMSD : public G4VSensitiveDetector
{
public:
  SiPMSD(const G4String& name, const G4String& hcName);
  ~SiPMSD() override = default;

  void   Initialize  (G4HCofThisEvent* hce) override;
  G4bool ProcessHits (G4Step* step, G4TouchableHistory* history) override;
  void   EndOfEvent  (G4HCofThisEvent* hce) override;

private:
  HodoscopeHitsCollection* fHC = nullptr;
  G4int                    fHCID = -1;
  std::array<G4int, 32>    fIndex {};
};

#endif
