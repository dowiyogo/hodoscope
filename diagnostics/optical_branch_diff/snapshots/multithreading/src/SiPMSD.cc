//----------------------------------------------------------------------------
// SiPMSD.cc
//----------------------------------------------------------------------------
#include "SiPMSD.hh"

#include "G4HCofThisEvent.hh"
#include "G4SDManager.hh"
#include "G4Step.hh"
#include "G4TouchableHistory.hh"
#include "G4OpticalPhoton.hh"
#include "G4SystemOfUnits.hh"

SiPMSD::SiPMSD(const G4String& name, const G4String& hcName)
: G4VSensitiveDetector(name)
{
  collectionName.insert(hcName);
}

void SiPMSD::Initialize(G4HCofThisEvent* hce)
{
  fHC = new HodoscopeHitsCollection(SensitiveDetectorName, collectionName[0]);
  if (fHCID < 0)
    fHCID = G4SDManager::GetSDMpointer()->GetCollectionID(collectionName[0]);
  hce->AddHitsCollection(fHCID, fHC);

  for (G4int i = 0; i < 32; ++i) {
    auto* h = new HodoscopeHit();
    h->type   = HitType::kSiPM;
    h->copyNo = i;
    fIndex[i] = fHC->insert(h) - 1;
  }
}

G4bool SiPMSD::ProcessHits(G4Step* step, G4TouchableHistory*)
{
  // Sólo contamos opticalphotons. Cualquier otra partícula que cruza el SiPM
  // (delta-rays, etc.) la ignoramos; el SiPM real es una superficie óptica.
  auto* def = step->GetTrack()->GetDefinition();
  if (def != G4OpticalPhoton::Definition()) return false;

  auto* tk     = step->GetPreStepPoint()->GetTouchable();
  G4int copyNo = tk->GetCopyNumber(0);
  if (copyNo < 0 || copyNo >= 32) return false;

  auto* hit = (*fHC)[fIndex[copyNo]];
  ++(hit->nPhotons);

  // El fotón es absorbido por el SiPM (modelo de "absorbedor perfecto").
  step->GetTrack()->SetTrackStatus(fStopAndKill);
  return true;
}

void SiPMSD::EndOfEvent(G4HCofThisEvent*) {}
