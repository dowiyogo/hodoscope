//----------------------------------------------------------------------------
// ScintillatorSD.hh
//
// Sensitive detector para las 32 barras de centellador.
// Acumula edep por barra (copyNo). Mantiene una lista interna indexada
// por copyNo para ser eficiente: hits[copyNo] += edep en cada step.
//----------------------------------------------------------------------------
#ifndef HODOSCOPE_SCINTILLATOR_SD_HH
#define HODOSCOPE_SCINTILLATOR_SD_HH

#include "G4VSensitiveDetector.hh"
#include "HodoscopeHit.hh"
#include <array>

class G4Step;
class G4HCofThisEvent;

class ScintillatorSD : public G4VSensitiveDetector
{
public:
  ScintillatorSD(const G4String& name, const G4String& hcName);
  ~ScintillatorSD() override = default;

  void   Initialize  (G4HCofThisEvent* hce) override;
  G4bool ProcessHits (G4Step* step, G4TouchableHistory* history) override;
  void   EndOfEvent  (G4HCofThisEvent* hce) override;

private:
  HodoscopeHitsCollection* fHC = nullptr;
  G4int                    fHCID = -1;
  // tabla rápida copyNo → índice en la collection
  std::array<G4int, 32>    fIndex {};
};

#endif
