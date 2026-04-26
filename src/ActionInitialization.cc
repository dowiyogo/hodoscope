#include "ActionInitialization.hh"
#include "PrimaryGeneratorAction.hh"
#include "RunAction.hh"
#include "EventAction.hh"

void ActionInitialization::BuildForMaster() const
{
  SetUserAction(new RunAction());
}

void ActionInitialization::Build() const
{
  SetUserAction(new PrimaryGeneratorAction());

  auto* runAction   = new RunAction();
  auto* eventAction = new EventAction(runAction);

  SetUserAction(runAction);
  SetUserAction(eventAction);
}
