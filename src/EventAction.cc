//----------------------------------------------------------------------------
// EventAction.cc
//----------------------------------------------------------------------------
#include "EventAction.hh"
#include "RunAction.hh"
#include "HodoscopeHit.hh"

#include "G4Event.hh"
#include "G4HCofThisEvent.hh"
#include "G4SDManager.hh"
#include "G4AnalysisManager.hh"
#include "G4PrimaryVertex.hh"
#include "G4PrimaryParticle.hh"
#include "G4SystemOfUnits.hh"

EventAction::EventAction(RunAction* runAction)
: G4UserEventAction(), fRunAction(runAction) {}

void EventAction::BeginOfEventAction(const G4Event*) {}

void EventAction::EndOfEventAction(const G4Event* event)
{
  // ----- Resolver IDs de las hits collections (una vez) --------------------
  if (fScintHCID < 0) {
    auto* sdm = G4SDManager::GetSDMpointer();
    fScintHCID = sdm->GetCollectionID("ScintHC");
    fSiPMHCID  = sdm->GetCollectionID("SiPMHC");
  }

  auto* HCE = event->GetHCofThisEvent();
  if (!HCE) return;

  auto* scintHC = static_cast<HodoscopeHitsCollection*>(HCE->GetHC(fScintHCID));
  auto* sipmHC  = static_cast<HodoscopeHitsCollection*>(HCE->GetHC(fSiPMHCID));

  // ----- Llenar TTree ------------------------------------------------------
  auto* an = G4AnalysisManager::Instance();
  G4int col = 0;

  an->FillNtupleIColumn(col++, event->GetEventID());

  // primario
  G4double px=0, py=0, pz=0, x=0, y=0, z=0, E=0;
  if (event->GetNumberOfPrimaryVertex() > 0) {
    auto* v = event->GetPrimaryVertex(0);
    x = v->GetX0()/mm; y = v->GetY0()/mm; z = v->GetZ0()/mm;
    if (v->GetNumberOfParticle() > 0) {
      auto* p = v->GetPrimary(0);
      auto mom = p->GetMomentum();
      G4double pmag = mom.mag();
      if (pmag > 0) {
        px = mom.x()/pmag; py = mom.y()/pmag; pz = mom.z()/pmag;
      }
      E = p->GetKineticEnergy()/MeV;
    }
  }
  an->FillNtupleDColumn(col++, x);
  an->FillNtupleDColumn(col++, y);
  an->FillNtupleDColumn(col++, z);
  an->FillNtupleDColumn(col++, px);
  an->FillNtupleDColumn(col++, py);
  an->FillNtupleDColumn(col++, pz);
  an->FillNtupleDColumn(col++, E);

  // edep[32]
  for (int i = 0; i < 32; ++i) {
    G4double eMeV = 0.;
    if (scintHC && i < (int)scintHC->entries())
      eMeV = (*scintHC)[i]->edep / MeV;
    an->FillNtupleDColumn(col++, eMeV);
  }

  // nph[32]
  for (int i = 0; i < 32; ++i) {
    G4int nph = 0;
    if (sipmHC && i < (int)sipmHC->entries())
      nph = (*sipmHC)[i]->nPhotons;
    an->FillNtupleIColumn(col++, nph);
  }

  // tfirst[32]
  for (int i = 0; i < 32; ++i) {
    G4double t = 0.;
    if (scintHC && i < (int)scintHC->entries())
      t = (*scintHC)[i]->tFirst / ns;
    an->FillNtupleDColumn(col++, t);
  }

  an->AddNtupleRow();
}
