//----------------------------------------------------------------------------
// ScintillatorSD.cc
//----------------------------------------------------------------------------
#include "ScintillatorSD.hh"

#include "G4HCofThisEvent.hh"
#include "G4SDManager.hh"
#include "G4Step.hh"
#include "G4TouchableHistory.hh"
#include "G4SystemOfUnits.hh"

ScintillatorSD::ScintillatorSD(const G4String& name, const G4String& hcName)
: G4VSensitiveDetector(name)
{
  collectionName.insert(hcName);
}

void ScintillatorSD::Initialize(G4HCofThisEvent* hce)
{
  fHC = new HodoscopeHitsCollection(SensitiveDetectorName, collectionName[0]);
  if (fHCID < 0) {
    fHCID = G4SDManager::GetSDMpointer()
              ->GetCollectionID(collectionName[0]);
  }
  hce->AddHitsCollection(fHCID, fHC);

  // Pre-llenar 32 hits vacíos, uno por barra. Así indexamos por copyNo
  // sin tener que buscar.
  for (G4int i = 0; i < 32; ++i) {
    auto* h = new HodoscopeHit();
    h->type   = HitType::kBar;
    h->copyNo = i;
    fIndex[i] = fHC->insert(h) - 1;   // G4THitsCollection::insert retorna size
  }
}

G4bool ScintillatorSD::ProcessHits(G4Step* step, G4TouchableHistory*)
{
  G4double edep = step->GetTotalEnergyDeposit();
  if (edep <= 0.) return false;

  // copyNo de la barra (asignado en G4PVPlacement)
  auto* tk     = step->GetPreStepPoint()->GetTouchable();
  G4int copyNo = tk->GetCopyNumber(0);
  if (copyNo < 0 || copyNo >= 32) return false;

  auto* hit = (*fHC)[fIndex[copyNo]];

  if (hit->edep == 0.) {
    hit->posEntry = step->GetPreStepPoint()->GetPosition();
    hit->tFirst   = step->GetPreStepPoint()->GetGlobalTime();
  }
  hit->posExit = step->GetPostStepPoint()->GetPosition();
  hit->edep   += edep;

  return true;
}

void ScintillatorSD::EndOfEvent(G4HCofThisEvent*) { /* nada extra */ }
