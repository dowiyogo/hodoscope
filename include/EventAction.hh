//----------------------------------------------------------------------------
// EventAction.hh
//
// Recolecta hits del evento, llena las columnas del TTree.
//----------------------------------------------------------------------------
#ifndef HODOSCOPE_EVENT_ACTION_HH
#define HODOSCOPE_EVENT_ACTION_HH

#include "G4UserEventAction.hh"
#include "globals.hh"

class RunAction;
class G4Event;

class EventAction : public G4UserEventAction
{
public:
  explicit EventAction(RunAction* runAction);
  ~EventAction() override = default;

  void BeginOfEventAction(const G4Event* event) override;
  void EndOfEventAction  (const G4Event* event) override;

private:
  RunAction* fRunAction;
  G4int      fScintHCID = -1;
  G4int      fSiPMHCID  = -1;
};

#endif
